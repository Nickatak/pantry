/**
 * BARCODE MODULE STRUCTURE
 *
 * This module is organized into logical concerns:
 *
 * ├── utils/
 * │   ├── audioUtils.ts      - Web Audio API for detection beeping
 * │   ├── canvasUtils.ts     - Canvas operations for frame capturing & visualization
 * │   ├── barcodeApi.ts      - API calls for barcode processing
 * │   └── index.ts           - Barrel export for clean imports
 * │
 * ├── hooks/
 * │   ├── useCamera.ts           - Camera stream initialization & BarcodeDetector detection
 * │   ├── useDetectionFeedback.ts- Visual/audio feedback on detection
 * │   ├── useHtml5Scanner.ts     - Html5QrcodeScanner lifecycle management
 * │   ├── useBarcodeScannerState.ts - Barcode state & processing logic
 * │   └── index.ts               - Barrel export for clean imports
 * │
 * ├── components/
 * │   ├── ErrorDisplay.tsx   - Error message rendering
 * │   ├── CameraView.tsx     - Camera feed & capture controls
 * │   ├── ResultsView.tsx    - Barcode result display
 * │   └── index.ts           - Barrel export for clean imports
 * │
 * └── page.tsx               - Main page component
 *     └── 50 lines (originally 550+)
 *
 * BENEFITS OF THIS STRUCTURE:
 * ✓ Single Responsibility: Each hook/component has one clear purpose
 * ✓ Testability: Easy to unit test individual hooks and utilities
 * ✓ Reusability: Hooks/utilities can be used in other components
 * ✓ Maintainability: Changes are localized to specific modules
 * ✓ Readability: Main page is now focused on composition, not logic
 */
