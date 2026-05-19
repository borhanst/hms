#!/bin/bash
# Quick script to rebuild the HMS demo video

echo "🎬 Rebuilding HMS Demo Video..."
echo ""

# Render the video
npx remotion render HMSDemo out/demo.mp4

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Video rendered successfully!"
    echo "📁 Output: out/demo.mp4"
    echo "📏 Size: $(ls -lh out/demo.mp4 | awk '{print $5}')"
else
    echo ""
    echo "❌ Render failed. Check the errors above."
    exit 1
fi
