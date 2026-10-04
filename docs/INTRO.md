# Liminal scroll introduction — 4 October 2026

User-requested entrance inspired by the supplied monochrome robot/human hand reference. Scope is the introduction only; the operational dashboard retains its existing design and saved evidence.

- `/`: intro plus real server-rendered overview beneath it. Words fade through the first half of scroll, hands meet at 76% progress, dashboard fades in at 80–99%. Completion releases scrolling and changes the URL to `/workspace` without an evaluation or page reload.
- `/workspace`: direct overview, preserving filters and saved results. Shared home/sidebar links bypass the intro. Refresh after entry stays in the workspace.
- Enter workspace / keyboard skip bypass the animation and focus the main content. With reduced motion or no JavaScript, the static intro and ordinary entry link remain usable. No wheel/touch interception.
- Intro-specific CSS/JS, local Manrope font, off-white paper/noise treatment, black type and generated grayscale hand artwork. Existing product styles are unchanged.
- Asset: `design-preview/assets/intro-hands.png`, generated with the built-in image generation tool, transparent PNG, retained in the repository. Both clipped halves share one image plane for fingertip alignment; no runtime external asset request.
- Generation prompt: wide transparent monochrome editorial photograph of a detailed skeletal robotic arm entering from the left and a human hand entering from the right, index fingers reaching toward each other at matching height, other fingers curled naturally; silver metal and grayscale skin with newspaper stipple/halftone grain; arms extend beyond outer edges, empty space above, no text/logo/background. Output copied without modifying the generated artwork; alpha preserved.

Verification: 92 Python tests pass; `node tests/check_intro.cjs` passes reduced-motion, explicit keyboard skip, contact-before-reveal and completion guards; JS syntax and Django checks clean. Browser desktop and mobile inspected, scroll fade/contact/dashboard verified, explicit entry and refresh verified. No Gemini evaluation requests or fixture resets. P-07 remains externally quota-blocked.

The Impeccable context executable was unavailable (engine not installed / cache permission); existing project context was read directly. No detector result is claimed.
