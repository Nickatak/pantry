/**
 * CSS styles for html5-qrcode scanner container customization
 * Hides UI elements and makes the video feed fill the entire container
 *
 * The html5-qrcode library creates several DOM elements by default:
 * - Dashboard section with input type selection
 * - Branding watermarks
 * - Info icons
 *
 * These styles override the default layout to create a clean, full-screen
 * scanning experience without unnecessary UI elements.
 *
 * LAYOUT STRUCTURE:
 * #barcode-scanner-container (main container)
 *   └── #barcode-scanner-container__scan_region (scanning region)
 *       └── #barcode-scanner-container__scan_region_video (video wrapper)
 *           └── video element
 *   └── #barcode-scanner-container__dashboard (hidden)
 */
export const html5QrcodeScannerStyles = `
  /* Main container - flex layout to fill available space */
  #barcode-scanner-container {
    display: flex !important;
    flex-direction: column !important;
    min-height: 400px !important;
  }

  /* Hide dashboard/input type selection section */
  #barcode-scanner-container__dashboard {
    display: none !important;
  }

  /* Scan region - flex child that expands to fill available space */
  #barcode-scanner-container__scan_region {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
  }

  /* Video wrapper - stretches to fill parent and maintains aspect ratio */
  #barcode-scanner-container__scan_region video {
    flex: 1 !important;
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
  }

  /* Hide html5-qrcode branding line */
  .html5-qrcode-element-br-line {
    display: none !important;
  }

  /* Hide only the small info icon watermark (top-right corner) */
  #barcode-scanner-container__scan_region img.html5-qrcode-element {
    display: none !important;
  }
`;
