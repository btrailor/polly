"""
BudgetManager - API usage tracking and budget enforcement.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class UsageRecord:
    """A single API usage record."""
    id: Optional[int]
    timestamp: datetime
    provider: str
    model: str
    task_type: Optional[str]
    tokens_in: int
    tokens_out: int
    cost: float
    conversation_id: Optional[int] = None


@dataclass
class SpendingSummary:
    """Summary of spending over a period."""
    total_cost: float
    total_requests: int
    total_tokens_in: int
    total_tokens_out: int
    by_provider: Dict[str, float]
    by_model: Dict[str, float]


class BudgetManager:
    """Manages API usage tracking and budget enforcement."""

    DEFAULT_DAILY_LIMIT = 10.0
    DEFAULT_MONTHLY_LIMIT = 200.0
    DEFAULT_WARN_THRESHOLD = 0.8

    def __init__(
        self,
        db_path: Optional[Path] = None,
        daily_limit: float = DEFAULT_DAILY_LIMIT,
        monthly_limit: float = DEFAULT_MONTHLY_LIMIT,
        warn_threshold: float = DEFAULT_WARN_THRESHOLD
    ):
        self.db_path = db_path or Path.home() / '.polly' / 'usage.db'
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.warn_threshold = warn_threshold
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._warned_daily = False
        self._warned_monthly = False

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    task_type TEXT,
                    tokens_in INTEGER NOT NULL,
                    tokens_out INTEGER NOT NULL,
                    cost REAL NOT NULL,
                    conversation_id INTEGER,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON api_usage(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_provider ON api_usage(provider)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_date ON api_usage(date(timestamp))")
            conn.commit()
            logger.info(f"Initialized budget database at {self.db_path}")

    async def check_budget(self, estimated_cost: float) -> bool:
        daily_spent = await self.get_daily_spending()
        monthly_spent = await self.get_monthly_spending()
        if daily_spent + estimated_cost > self.daily_limit:
            logger.warning(f"Daily budget exceeded: ${daily_spent:.2f} + ${estimated_cost:.2f} > ${self.daily_limit:.2f}")
            return False
        if monthly_spent + estimated_cost > self.monthly_limit:
            logger.warning(f"Monthly budget exceeded: ${monthly_spent:.2f} + ${estimated_cost:.2f} > ${self.monthly_limit:.2f}")
            return False
        daily_usage_pct = (daily_spent + estimated_cost) / self.daily_limit
        monthly_usage_pct = (monthly_spent + estimated_cost) / self.monthly_limit
        if daily_usage_pct >= self.warn_threshold and not self._warned_daily:
            logger.warning(f"Daily budget at {daily_usage_pct*100:.0f}%: ${daily_spent:.2f}/${self.daily_limit:.2f}")
            self._warned_daily = True
        if monthly_usage_pct >= self.warn_threshold and not self._warned_monthly:
            logger.warning(f"Monthly budget at {monthly_usage_pct*100:.0f}%: ${monthly_spent:.2f}/${self.monthly_limit:.2f}")
            self._warned_monthly = True
        return True

    async def record_usage(
        self,
        provider: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        cost: float,
        task_type: Optional[str] = None,
        conversation_id: Optional[int] = None
    ) -> int:
        record = UsageRecord(
            id=None, timestamp=datetime.now(), provider=provider, model=model,
            task_type=task_type, tokens_in=tokens_in, tokens_out=tokens_out,
            cost=cost, conversation_id=conversation_id
        )
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_usage
                (timestamp, provider, model, task_type, tokens_in, tokens_out, cost, conversation_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (record.timestamp, record.provider, record.model, record.task_type,
                  record.tokens_in, record.tokens_out, record.cost, record.conversation_id))
            conn.commit()
            record_id = cursor.lastrowid
        logger.info(f"Recorded usage: {provider}/{model} - in={tokens_in}, out={tokens_out}, cost=${cost:.4f}")
        return record_id

    async def get_daily_spending(self, date: Optional[datetime] = None) -> float:
        if date is None:
            date = datetime.now()
        date_str = date.strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(cost), 0) FROM api_usage WHERE date(timestamp) = ?", (date_str,))
            result = cursor.fetchone()
        return result[0] if result else 0.0

    async def get_monthly_spending(self, year: Optional[int] = None, month: Optional[int] = None) -> float:
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        first_day = datetime(year, month, 1)
        last_day = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(cost), 0) FROM api_usage WHERE timestamp >= ? AND timestamp < ?", (first_day, last_day))
            result = cursor.fetchone()
        return result[0] if result else 0.0

    async def get_spending_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> SpendingSummary:
        if start_date is None:
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1)
        if end_date is None:
            end_date = datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(cost), 0), COUNT(*), COALESCE(SUM(tokens_in), 0), COALESCE(SUM(tokens_out), 0)
                FROM api_usage WHERE timestamp >= ? AND timestamp <= ?
            """, (start_date, end_date))
            totals = cursor.fetchone()
            cursor.execute("SELECT provider, COALESCE(SUM(cost), 0) FROM api_usage WHERE timestamp >= ? AND timestamp <= ? GROUP BY provider", (start_date, end_date))
            by_provider = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.execute("SELECT model, COALESCE(SUM(cost), 0) FROM api_usage WHERE timestamp >= ? AND timestamp <= ? GROUP BY model", (start_date, end_date))
            by_model = {row[0]: row[1] for row in cursor.fetchall()}
        return SpendingSummary(
            total_cost=totals[0], total_requests=totals[1], total_tokens_in=totals[2], total_tokens_out=totals[3],
            by_provider=by_provider, by_model=by_model
        )

    async def get_usage_history(
        self,
        limit: int = 100,
        provider: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[UsageRecord]:
        query, params = "SELECT * FROM api_usage WHERE 1=1", []
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            records = [
                UsageRecord(id=row[0], timestamp=datetime.fromisoformat(row[1]), provider=row[2], model=row[3],
                            task_type=row[4], tokens_in=row[5], tokens_out=row[6], cost=row[7], conversation_id=row[8])
                for row in cursor.fetchall()
            ]
        return records

    async def reset_warnings(self):
        self._warned_daily = False
        self._warned_monthly = False

    async def get_budget_status(self) -> Dict[str, Any]:
        daily_spent = await self.get_daily_spending()
        monthly_spent = await self.get_monthly_spending()
        return {
            'daily': {'spent': daily_spent, 'limit': self.daily_limit, 'remaining': self.daily_limit - daily_spent,
                      'percent_used': (daily_spent / self.daily_limit * 100) if self.daily_limit > 0 else 0},
            'monthly': {'spent': monthly_spent, 'limit': self.monthly_limit, 'remaining': self.monthly_limit - monthly_spent,
                        'percent_used': (monthly_spent / self.monthly_limit * 100) if self.monthly_limit > 0 else 0},
            'warn_threshold': self.warn_threshold * 100
        }

    async def export_usage_csv(
        self,
        output_path: Path,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        import csv
        records = await self.get_usage_history(limit=100000, start_date=start_date, end_date=end_date)
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'provider', 'model', 'task_type', 'tokens_in', 'tokens_out', 'total_tokens', 'cost'])
            for record in records:
                writer.writerow([record.timestamp.isoformat(), record.provider, record.model, record.task_type or '',
                                 record.tokens_in, record.tokens_out, record.tokens_in + record.tokens_out, f"{record.cost:.6f}"])
        logger.info(f"Exported {len(records)} usage records to {output_path}")
