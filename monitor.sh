#!/bin/bash
# Monitor scraper progress

echo "======================================="
echo "  Avtotemir.az Scraper Monitor"
echo "======================================="
echo ""

# Check if scraper is running
if [ -f scraper.pid ]; then
    PID=$(cat scraper.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✓ Scraper is RUNNING (PID: $PID)"
    else
        echo "✗ Scraper is NOT running (PID $PID not found)"
    fi
else
    echo "✗ No PID file found"
fi

echo ""

# Show current progress
if [ -f scraper.log ]; then
    echo "--- Recent Activity (last 10 lines) ---"
    tail -10 scraper.log
    echo ""

    # Count completed pages
    PAGES=$(grep "Completed page" scraper.log | tail -1)
    if [ ! -z "$PAGES" ]; then
        echo "--- Progress ---"
        echo "$PAGES"
    fi

    # Count total masters
    TOTAL=$(grep "Total masters scraped:" scraper.log | tail -1)
    if [ ! -z "$TOTAL" ]; then
        echo "$TOTAL"
    fi
else
    echo "No log file found yet"
fi

echo ""

# Show output files
if [ -f avtotemir_masters.json ] || [ -f avtotemir_masters.csv ]; then
    echo "--- Output Files ---"
    ls -lh avtotemir_masters.* 2>/dev/null
else
    echo "No output files created yet"
fi

echo ""
echo "======================================="
echo "Commands:"
echo "  Monitor live: tail -f scraper.log"
echo "  Stop scraper: kill \$(cat scraper.pid)"
echo "  Check status: ./monitor.sh"
echo "======================================="
