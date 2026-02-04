-- AppleScript to request Reminders permissions
-- This will trigger the macOS system permission dialog

tell application "Reminders"
	-- Simply accessing Reminders will trigger the permission request
	try
		set reminderListCount to count of lists
		display dialog "Reminders access granted! Found " & reminderListCount & " lists." buttons {"OK"} default button 1
	on error errMsg
		display dialog "Error accessing Reminders: " & errMsg buttons {"OK"} default button 1
	end try
end tell
