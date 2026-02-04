-- AppleScript to request Calendar permissions
-- This will trigger the macOS system permission dialog

tell application "Calendar"
	-- Simply accessing Calendar will trigger the permission request
	try
		set calendarCount to count of calendars
		display dialog "Calendar access granted! Found " & calendarCount & " calendars." buttons {"OK"} default button 1
	on error errMsg
		display dialog "Error accessing Calendar: " & errMsg buttons {"OK"} default button 1
	end try
end tell
