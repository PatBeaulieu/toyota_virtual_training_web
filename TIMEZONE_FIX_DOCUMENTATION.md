# Timezone Fix Documentation

## Problem
When creating a training session, the time entered was not displaying correctly on the region page. 

**Example Issue:**
- Admin creates a session for Pacific region
- Enters 2:00 PM (expecting it to display as 2:00 PM Pacific)
- Region page showed 11:00 AM Pacific instead ❌

## Root Cause
The form was storing the entered time directly as Eastern Time without considering the selected region. When the view converted it back to the region's timezone for display, it showed the wrong time.

**Old Flow (BROKEN):**
1. User enters: `2:00 PM` for Pacific region
2. System stores: `2:00 PM Eastern` (no conversion)
3. System displays: `2:00 PM Eastern → 11:00 AM Pacific` (converts on display)
4. Result: Shows `11:00 AM` instead of intended `2:00 PM` ❌

## Solution
The form now **automatically converts** from the regional timezone to Eastern Time before saving, so the time displays correctly.

**New Flow (FIXED):**
1. User enters: `2:00 PM` for Pacific region
2. Form converts: `2:00 PM Pacific → 5:00 PM Eastern` ✓
3. System stores: `5:00 PM Eastern`
4. System displays: `5:00 PM Eastern → 2:00 PM Pacific` (converts on display)
5. Result: Shows `2:00 PM` as intended ✓

## Implementation Details

### 1. Form Label (Dynamic)
The form label now changes based on the selected region:
- Atlantic → "Training Time (Atlantic Time) *"
- Pacific → "Training Time (Pacific Time) *"
- Quebec → "Training Time (Eastern Time) *"

### 2. Help Text (Clear)
```
Enter the time in [Region] Time ([Timezone Abbr]) for [Region Name]
The time you enter will be displayed as-is on the region's page.
```

### 3. Form Conversion Logic (`forms.py`)

**On Save (clean method):**
```python
def clean(self):
    # Get entered time and selected region
    time_est = cleaned_data.get('time_est')
    training_page = cleaned_data.get('training_page')
    
    # Convert from regional time to Eastern time
    regional_datetime = regional_tz.localize(datetime.combine(date.today(), time_est))
    eastern_datetime = regional_datetime.astimezone(eastern_tz)
    
    # Store Eastern time in database
    cleaned_data['time_est'] = eastern_datetime.time()
```

**On Edit (__init__ method):**
```python
if self.instance and self.instance.pk and self.instance.time_est and self.instance.training_page:
    # Convert stored Eastern time back to regional time for display
    eastern_datetime = eastern_tz.localize(datetime.combine(date.today(), self.instance.time_est))
    regional_datetime = eastern_datetime.astimezone(regional_tz)
    
    # Show regional time in form
    self.initial['time_est'] = regional_datetime.time().strftime('%H:%M')
```

### 4. Timezone Mappings

| Region   | Timezone Database Value | Offset from Eastern |
|----------|-------------------------|---------------------|
| Atlantic | America/Halifax         | +1 hour             |
| Quebec   | America/Toronto         | 0 hours             |
| Central  | America/Toronto         | 0 hours             |
| Prairie  | America/Winnipeg        | -1 hour             |
| Pacific  | America/Vancouver       | -3 hours            |

## How to Use

### Creating a New Session

1. **Select the region** (e.g., Pacific)
2. **Notice the label changes** to "Training Time (Pacific Time)"
3. **Enter the time as it should appear** on the Pacific page (e.g., 2:00 PM)
4. **Save** - the form automatically converts 2:00 PM Pacific → 5:00 PM Eastern
5. **Verify** - check the Pacific region page, it shows 2:00 PM ✓

### Editing an Existing Session

1. **Open the session** for editing
2. **Notice the time shown** is in the region's timezone (not Eastern)
3. **Modify if needed** - enter the time as it should appear on the region page
4. **Save** - the form converts to Eastern time automatically
5. **Verify** - check the region page, it shows your entered time ✓

## Examples

### Example 1: Pacific Region Session at 10:00 AM
- **Want to display**: 10:00 AM Pacific
- **Enter in form**: 10:00 AM (form shows "Pacific Time")
- **System stores**: 1:00 PM Eastern (automatic conversion)
- **Displays on page**: 10:00 AM PST ✓

### Example 2: Atlantic Region Session at 3:00 PM
- **Want to display**: 3:00 PM Atlantic
- **Enter in form**: 3:00 PM (form shows "Atlantic Time")
- **System stores**: 2:00 PM Eastern (automatic conversion)
- **Displays on page**: 3:00 PM AST ✓

### Example 3: Quebec Session at 2:00 PM
- **Want to display**: 2:00 PM Eastern
- **Enter in form**: 2:00 PM (form shows "Eastern Time")
- **System stores**: 2:00 PM Eastern (no conversion needed)
- **Displays on page**: 2:00 PM EST ✓

## Files Changed

### `/training_app/forms.py`
- Updated `SimpleTrainingSessionForm.__init__()` to convert stored Eastern time to regional time when editing
- Added `SimpleTrainingSessionForm.clean()` method to convert entered regional time to Eastern time before saving

### `/training_app/templates/training_app/simple_admin/create_session.html`
- Updated time field label to be dynamic based on selected region
- Updated help text to clearly state "enter time for the selected region"
- Updated JavaScript to dynamically change label and help text when region changes

### `/training_app/templates/training_app/simple_admin/edit_session.html`
- Same changes as create_session.html

## Testing

### Manual Test Cases

**Test 1: Create Pacific Session**
1. Create session for Pacific at 2:00 PM
2. Expected: Displays as 2:00 PM PST on Pacific page

**Test 2: Create Atlantic Session**
1. Create session for Atlantic at 2:00 PM
2. Expected: Displays as 2:00 PM AST on Atlantic page

**Test 3: Edit Existing Session**
1. Open existing Pacific session showing 2:00 PM
2. Form should show 2:00 PM Pacific (not the Eastern time)
3. Change to 3:00 PM and save
4. Expected: Displays as 3:00 PM PST on Pacific page

**Test 4: Region Change Detection**
1. Start creating a session
2. Select Pacific - label should say "Training Time (Pacific Time)"
3. Change to Atlantic - label should update to "Training Time (Atlantic Time)"

## Migration Notes

- **No database migration required** - only form logic changed
- **Existing sessions** will work correctly when edited (form converts on load)
- **Backward compatible** - display logic unchanged

## Troubleshooting

**Issue**: Time still displays incorrectly
- **Check**: Make sure you're using the updated form (label should show region's timezone)
- **Fix**: Edit the session and re-save it with the new form

**Issue**: Form shows Eastern time when editing
- **Check**: The session must have a valid training_page assigned
- **Fix**: Make sure the training_page field is properly set

## Technical Notes

- Database field `TrainingSession.time_est` continues to store Eastern Time
- All timezone conversions use `pytz` library
- Conversions use dummy date (`date.today()`) since we only care about time
- Display logic in views remains unchanged (already converts Eastern → Regional)

