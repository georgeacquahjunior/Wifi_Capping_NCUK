# WiFi Capping System - NCUK

A secure web application for monitoring and managing WiFi data usage for the North Consortium UK (NCUK).

## Features

- **Real-time WiFi Usage Monitoring**: Track current data consumption
- **Data Cap Management**: Set and modify data usage limits
- **Usage Analytics**: Visual dashboard for usage statistics
- **Secure Implementation**: Comprehensive Content Security Policy (CSP) headers

## Security

This application implements robust security measures including:

- **Content Security Policy (CSP)** headers to prevent XSS attacks
- **Multiple deployment platform support** (Vercel, Netlify, Apache)
- **HTTPS enforcement** via HSTS headers
- **Clickjacking protection** through frame-ancestors policy
- **Additional security headers** for comprehensive protection

See [SECURITY.md](SECURITY.md) for detailed security implementation documentation.

## Deployment

The application supports multiple deployment platforms with automatic CSP header configuration:

### Vercel
```bash
vercel deploy
```
CSP headers are configured via `vercel.json`

### Netlify
```bash
netlify deploy
```
CSP headers are configured via `netlify.toml`

### Apache/Traditional Hosting
Upload files to your web server. CSP headers are configured via `.htaccess`

### GitHub Pages
The application can be deployed to GitHub Pages with CSP headers set via HTML meta tags.

## Development

1. Clone the repository
2. Open `index.html` in a web browser
3. The application will work locally with simulated data

## CSP Compliance

The application is designed to be fully compliant with strict Content Security Policy:

- No inline scripts without nonces
- Restricted resource loading
- Frame protection
- Secure defaults

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure CSP compliance
5. Submit a pull request

## License

This project is licensed under the MIT License.