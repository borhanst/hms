# HMS Demo Video (Remotion)

This directory contains a demo video for the Hospital Management System, built with Remotion.

## Video Details

- **Resolution:** 1920x1080 (Full HD)
- **Frame Rate:** 30 fps
- **Duration:** ~15 seconds
- **File Size:** 1.7 MB
- **Codec:** H.264

## Video Structure

The video showcases the following HMS features:

1. **Intro Title** - Hospital Management System overview
2. **Login Screen** - Clean login interface with demo credentials
3. **Dashboard** - Real-time statistics cards and interactive charts
4. **Doctor Management** - Doctor profiles with specialization and availability
5. **Patient Records** - Comprehensive patient demographics and medical history
6. **Diagnostic Reports** - Lab test tracking with status management
7. **Prescriptions** - Digital prescriptions with medicine details
8. **Outro** - Technology stack showcase

## Project Structure

```
src/
├── Components.tsx    # Reusable UI components (FadeIn, SlideIn, MockBrowserFrame)
├── Screens.tsx       # Mock HMS screen components
├── Video.tsx         # Main video composition with transitions
├── Root.tsx          # Remotion root composition registration
└── index.ts          # Entry point
```

## Commands

```bash
# Preview in Remotion Studio (interactive)
npm run dev

# Render the video
npm run build

# The video will be output to: out/demo.mp4
```

## Features Highlighted

- **Role-based access control** (Admin, Doctor, Receptionist, etc.)
- **HTMX-powered dynamic UI** updates
- **Modern dark theme** with responsive design
- **Interactive charts** (Chart.js integration)
- **Status badges** with color coding
- **Comprehensive CRUD** operations

## Tech Stack Shown

- Django 5.2+
- HTMX 2.x
- Alpine.js 3.x
- SQLite

## Customization

To modify the video:

1. Edit `src/Video.tsx` to change scene durations or add/remove scenes
2. Edit `src/Screens.tsx` to modify individual screen mockups
3. Edit `src/Components.tsx` to change animation utilities
4. Re-render with `npm run build`

## Scene Timing

Each screen displays for ~4 seconds with 2-second title cards and smooth transitions (0.5s fade/slide effects).
