// Mock expo-haptics — no-op functions
export const impactAsync = jest.fn(async () => {});
export const notificationAsync = jest.fn(async () => {});
export const selectionAsync = jest.fn(async () => {});

export const ImpactFeedbackStyle = {
  Light: 'light',
  Medium: 'medium',
  Heavy: 'heavy',
  Rigid: 'rigid',
  Soft: 'soft',
};

export const NotificationFeedbackType = {
  Success: 'success',
  Warning: 'warning',
  Error: 'error',
};
