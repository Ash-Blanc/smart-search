# Smart Search Reflex App

This is the Reflex-based web interface for Smart Search, featuring an improved UI/UX with responsive design.

## Features

- Modern web interface built with Reflex
- Real-time search with progress indicators
- Responsive design that works on desktop and mobile
- Advanced search options (depth, confidence thresholds)
- State management handled by Reflex
- Easy deployment options

## UI/UX Improvements

### 1. Enhanced Visual Design
- Gradient headers and improved typography
- Card-based results display with proper spacing
- Confidence badges with color coding
- Better button styling and hover effects
- Consistent color scheme and visual hierarchy

### 2. Advanced Search Options
- Search depth selection (Quick, Standard, Deep)
- Confidence threshold slider
- Toggle options for sources and reasoning
- Collapsible advanced options panel

### 3. Responsive Design
- Mobile-first approach with adaptive layouts
- Flexible grid system that adjusts to screen size
- Appropriate font sizing for different devices
- Touch-friendly controls and buttons
- Optimized spacing and padding for mobile

### 4. Performance Optimizations
- Smooth animations and transitions
- Efficient component rendering
- Minimal re-renders with proper state management
- Optimized loading states

## Getting Started

1. Make sure you have all dependencies installed:
   ```bash
   pip install -e .
   ```

2. Initialize the Reflex app (if not already done):
   ```bash
   reflex init
   ```

3. Run the app:
   ```bash
   reflex run
   ```

Or use the main run script from the project root:
```bash
python run.py
```

## Development

To develop the app, you can modify `app.py` and the Reflex framework will automatically reload the changes.

## Deployment

For production deployment, you can build the app:
```bash
reflex export
```

This will create a static bundle that can be deployed to any web hosting service.