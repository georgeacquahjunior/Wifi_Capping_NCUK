# Security Configuration - CSP Headers

## Content Security Policy (CSP) Implementation

This project implements comprehensive Content Security Policy (CSP) headers to protect against various security threats including Cross-Site Scripting (XSS), code injection attacks, and data exfiltration.

### CSP Directives Implemented

#### Core Directives
- **`default-src 'self'`**: Only allows resources from the same origin by default
- **`script-src 'self' 'unsafe-inline'`**: Allows scripts from same origin and inline scripts (for compatibility)
- **`style-src 'self' 'unsafe-inline'`**: Allows styles from same origin and inline styles
- **`img-src 'self' data: https:`**: Allows images from same origin, data URLs, and HTTPS sources
- **`font-src 'self'`**: Only allows fonts from the same origin
- **`connect-src 'self'`**: Restricts AJAX, WebSocket, and EventSource connections to same origin

#### Security Directives
- **`frame-ancestors 'none'`**: Prevents the page from being embedded in frames (clickjacking protection)
- **`base-uri 'self'`**: Restricts the base URI to same origin
- **`form-action 'self'`**: Only allows form submissions to same origin
- **`object-src 'none'`**: Disables plugins like Flash
- **`upgrade-insecure-requests`**: Automatically upgrades HTTP requests to HTTPS

### Additional Security Headers

#### X-Frame-Options
- **Value**: `DENY`
- **Purpose**: Prevents clickjacking attacks by disallowing the page to be displayed in frames

#### X-Content-Type-Options
- **Value**: `nosniff`
- **Purpose**: Prevents MIME type sniffing attacks

#### Referrer-Policy
- **Value**: `strict-origin-when-cross-origin`
- **Purpose**: Controls how much referrer information is sent with requests

#### Permissions-Policy
- **Value**: `camera=(), microphone=(), geolocation=()`
- **Purpose**: Disables potentially sensitive APIs

#### Strict-Transport-Security (HSTS)
- **Value**: `max-age=31536000; includeSubDomains`
- **Purpose**: Enforces HTTPS connections

## Deployment Platform Support

### Vercel
Configuration file: `vercel.json`
- Headers are set via the headers configuration
- Automatically applied to all routes

### Netlify
Configuration file: `netlify.toml`
- Headers configured in TOML format
- Applied to all pages via `/*` matcher

### Apache (Traditional Hosting)
Configuration file: `.htaccess`
- Uses mod_headers module
- Includes additional file protection rules

### GitHub Pages
CSP headers are set via meta tags in HTML since GitHub Pages doesn't support custom headers configuration.

## Security Benefits

1. **XSS Prevention**: Strict script-src policy prevents unauthorized script execution
2. **Clickjacking Protection**: Frame-ancestors and X-Frame-Options prevent embedding attacks
3. **HTTPS Enforcement**: HSTS and upgrade-insecure-requests ensure secure connections
4. **Data Leakage Prevention**: Strict referrer and connect-src policies limit data exposure
5. **Plugin Security**: Object-src 'none' disables potentially vulnerable plugins

## Testing CSP

You can test the CSP implementation using:

1. Browser Developer Tools Console (check for CSP violations)
2. Online CSP analyzers like:
   - https://csp-evaluator.withgoogle.com/
   - https://observatory.mozilla.org/

## Maintenance

- Monitor CSP violation reports in browser console
- Update CSP policies when adding new third-party services
- Regularly review and tighten policies as the application evolves
- Consider implementing CSP violation reporting for production monitoring

## Compatibility Notes

- The current configuration uses 'unsafe-inline' for scripts and styles for compatibility
- For enhanced security, consider implementing nonce-based CSP in future iterations
- Some older browsers may not support all CSP directives