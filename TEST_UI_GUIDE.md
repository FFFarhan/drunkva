# DrunkVa Test UI Guide

## Quick Start

### Prerequisites
- Docker containers running (API on `http://localhost:8000`)
- Web browser

### Option 1: Direct Browser Access (Easiest)
1. Open `index.html` directly in your browser:
   - **Windows**: Double-click `index.html` or drag into browser
   - **Mac/Linux**: Right-click → Open With → Browser

2. The UI will automatically connect to the API at `http://localhost:8000`

### Option 2: Local Web Server
```powershell
cd C:\Users\Farhan\drunkva
python -m http.server 8080
```
Then visit: `http://localhost:8080`

---

## Testing Workflow

### 1. **Register a Test User** (Auth Tab)
- Click **Auth** tab → **Register**
- Fill in:
  - Username: `student_test`
  - Email: `student@example.com`
  - Password: `testpass123`
- Click **Register**
- ✅ You should see success message and auto-redirect to Log Drink

### 2. **Log Some Drinks** (Log Drink Tab)
- Select drink: Try "Kingfisher Premium (Bangalore)" or "Bira 91"
- Enter quantity: `12` oz (standard beer can)
- Optional notes: "First drink test"
- Watch **Standard Drinks** calculate in real-time using NIAAA formula
- Click **Log Drink**
- ✅ Should show success and standard drinks value

**Repeat 3-5 times with different drinks:**
- Try "Officer's Choice Whiskey" with 1.5 oz (shot)
- Try "Haywards 5000" with 12 oz
- Try budget beers like "Tuborg Premium"

### 3. **View Your History** (History Tab)
- Click **History** tab
- See all logged drinks with timestamps
- Try **Filter by days**: Enter `1` to see drinks from last 24 hours
- Click **Filter**
- ✅ Should see your recently logged drinks

### 4. **Check Leaderboard** (Leaderboard Tab)
- Click **Leaderboard** tab
- See **Global Leaderboard**: Top 25 users ranked by total drinks
- See **Your Rank**: Your position with nearby users (±5 context)
- Try changing **Show top**: 10 → 50 → 100
- ✅ Should show your position and nearby competitors

### 5. **View Profile** (Profile Tab)
- Click **Profile** tab
- See stat cards:
  - Total standard drinks logged
  - Number of drinks logged
  - Your leaderboard rank
  - Your username
- ✅ Stats should match what you logged

### 6. **Test Multi-User Leaderboard**
- Click **Logout** (top right)
- Register another user: `party_animal`
- Log 10+ drinks with higher quantities
- View leaderboard - should see new user ranked higher
- View personal rank - should show your position vs this user

---

## What's Being Tested

✅ **Backend API**
- User registration & authentication (JWT tokens)
- Drink type database (75 drinks available)
- Drink logging with NIAAA standard drink calculation
- Leaderboard ranking system
- User profile & statistics

✅ **Frontend UI**
- Tab navigation
- Form submission & validation
- Real-time calculations (standard drinks)
- API error handling
- Token-based authentication flow
- Responsive design

✅ **Database Integration**
- Bangalore/Mumbai student drinks loading
- Regional Indian drinks from all states
- Accurate ABV percentages
- Persistent data storage

---

## Available Test Drinks

### **Bangalore Student Favorites**
- Kingfisher Premium (4.2% ABV)
- Bira 91 Craft (4.2% ABV)
- Bangalore Blonde (5% ABV)
- Simba Stout (7.5% ABV)

### **Mumbai Student Favorites**
- Kingfisher Strong (8% ABV)
- Haywards 5000 (8% ABV)
- Imperial Blue Whiskey (42.8% ABV)
- Officer's Choice (42.8% ABV)

### **Budget Options**
- Tuborg (4.8% ABV)
- UB40 Malt (4% ABV)
- Bullets Whiskey (40% ABV)

### **Regional Indian Drinks**
- Cashew Feni (Goa - 42%)
- Apong (Northeast - 12%)
- Kallu (South - 8%)
- Mahua (Central - 30%)
- And 50+ more!

---

## Common Test Cases

### Standard Drink Calculation Examples
- 12 oz Kingfisher (4.2% ABV) = **~0.31 std drinks**
- 12 oz Haywards 5000 (8% ABV) = **~0.60 std drinks**
- 1.5 oz Officer's Choice (42.8% ABV) = **~1.13 std drinks**
- 2 oz Cashew Feni (42% ABV) = **~1.47 std drinks**

### Expected Leaderboard Behavior
- Each drink logged adds to total_drinks (sum of standard drinks)
- Rank calculated automatically (higher drinks = higher rank)
- Your Rank shows ±5 nearby users for competition context
- Last drink timestamp displayed for reference

---

## Troubleshooting

**"Cannot reach API" error?**
- Verify: `curl http://localhost:8000/health` returns `{"status":"ok"}`
- Check Docker containers: `docker-compose ps`
- Both containers should show `(healthy)`

**Drinks list empty?**
- Verify: `curl http://localhost:8000/drinks/types` returns 75 drinks
- Check database: `docker-compose logs db` for errors

**Login/Register fails?**
- Check browser console (F12) for error details
- Verify email format is correct
- Try username without special characters

**No leaderboard data?**
- Need multiple users logged in and drinks logged
- First time: register 2 different users and log drinks for each

---

## Next Steps After Testing

1. ✅ Verify all endpoints working correctly
2. ✅ Confirm standard drink calculations are accurate
3. ✅ Validate leaderboard ranking system
4. ✅ Test multi-user scenarios
5. → Ready for Flutter frontend development!

---

## File Structure
```
drunkva/
├── index.html          # Main UI (open this in browser!)
├── styles.css          # Styling & responsive design
├── app.js              # All API interactions & logic
├── app/                # Backend FastAPI code
├── docker-compose.yml  # Container orchestration
└── README.md           # This file
```

---

**Happy Testing! 🍺**
