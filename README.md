# WiFi Capping NCUK - Network Management System

A comprehensive WiFi bandwidth management and monitoring dashboard for NCUK (Northern Consortium of UK Universities) with a modern, consistent design system.

## 🎨 Design System Features

This project implements a comprehensive design system with improved UI consistency, featuring:

### Core Design Principles
- **Consistent Visual Language**: Unified color palette, typography, and spacing
- **Accessibility First**: WCAG 2.1 compliant with proper focus states and contrast ratios
- **Mobile Responsive**: Mobile-first design with breakpoint-based responsive utilities
- **Performance Optimized**: CSS custom properties for fast theme switching and minimal bundle size
- **Modern Browser Support**: CSS Grid, Flexbox, and modern CSS features

### Design System Components

#### 🎨 **Design Tokens (CSS Custom Properties)**
- **Colors**: Primary, secondary, semantic colors (success, warning, error, info)
- **Typography**: Font families, sizes, weights, and line heights
- **Spacing**: Consistent spacing scale from 4px to 96px
- **Shadows**: Elevation system with 6 shadow levels
- **Border Radius**: Consistent corner radius scale
- **Transitions**: Standardized animation timing

#### 🧩 **Component Library**
- **Buttons**: Multiple variants (primary, secondary, success, warning, error) with sizes
- **Forms**: Input fields, selects, textareas with validation states
- **Cards**: Interactive cards with headers, bodies, and footers
- **Badges**: Status indicators and labels
- **Alerts**: Contextual notifications
- **Metrics**: Data visualization components
- **Loading States**: Skeletons and spinners
- **Status Indicators**: Real-time status displays with animations

#### 🛠 **Utility Classes**
- **Typography**: Text sizes, weights, alignment, and colors
- **Layout**: Flexbox and Grid utilities
- **Spacing**: Margin and padding helpers
- **Colors**: Background and text color utilities
- **Borders**: Radius and style utilities
- **Shadows**: Box shadow utilities
- **Responsive**: Mobile-first responsive classes

### 🎯 **Advanced Features**

#### Accessibility
- **Focus Management**: Visible focus rings and proper tab order
- **Screen Reader Support**: Semantic HTML and ARIA labels
- **High Contrast Mode**: Automatic adaptation for high contrast preferences
- **Reduced Motion**: Respects user motion preferences

#### Progressive Enhancement
- **Dark Mode Support**: Automatic dark mode detection
- **Print Styles**: Optimized printing layouts
- **Glassmorphism Effects**: Modern backdrop blur effects
- **Advanced Animations**: Smooth micro-interactions

#### Developer Experience
- **CSS Custom Properties**: Easy theming and customization
- **Modular Structure**: Organized file structure for maintainability
- **Utility-First Approach**: Rapid development with utility classes
- **Component Documentation**: Clear examples and usage guidelines

## 🚀 Getting Started

### Prerequisites
- Node.js 16.0.0 or higher
- npm 8.0.0 or higher

### Installation
```bash
# Clone the repository
git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git

# Navigate to project directory
cd Wifi_Capping_NCUK

# Install dependencies
npm install

# Start development server
npm run dev
```

### Development Server
```bash
# Start local server on port 3000
npm run dev

# Start on custom port
npx serve . -p 8080
```

## 📁 Project Structure

```
src/
├── styles/
│   ├── design-system.css    # Core design tokens and base styles
│   ├── components.css       # Reusable component patterns
│   └── utilities.css        # Advanced utilities and helpers
├── components/              # React/JS components (future)
├── pages/                   # Page-specific styles
├── utils/                   # Helper functions
└── hooks/                   # Custom hooks (future)

public/                      # Static assets
index.html                   # Main application entry point
package.json                 # Project configuration
```

## 🎨 Design System Usage

### Basic Example
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">WiFi Status</h3>
  </div>
  <div class="card-body">
    <div class="status-indicator status-success">
      <div class="status-dot"></div>
      System Online
    </div>
  </div>
</div>
```

### Button Variations
```html
<button class="btn btn-primary">Primary Action</button>
<button class="btn btn-secondary btn-lg">Large Secondary</button>
<button class="btn btn-error btn-outline">Error Outline</button>
```

### Form Components
```html
<div class="form-group">
  <label class="form-label required">Username</label>
  <input type="text" class="form-input" placeholder="Enter username">
  <span class="form-help-text">Must be at least 3 characters</span>
</div>
```

### Utility Classes
```html
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <span class="text-lg font-semibold text-gray-900">Total Users</span>
  <span class="badge badge-primary">247</span>
</div>
```

## 🎯 User Categories & Features

### Student Access
- **Daily Limit**: 2-5 GB
- **Speed**: 5-10 Mbps
- **Session Management**: Standard monitoring

### Faculty Access  
- **Daily Limit**: 20 GB
- **Speed**: 50 Mbps
- **Priority Access**: Enhanced bandwidth allocation

### Guest Access
- **Session Limit**: 500 MB
- **Speed**: 2 Mbps
- **Time Limit**: 2-hour sessions

### Administrator Access
- **Unlimited**: No restrictions
- **Full Control**: Complete system management
- **Monitoring**: Real-time analytics

## 🔧 Development Tools

### Available Scripts
```bash
npm run start         # Start production server
npm run dev          # Start development server
npm run build        # Build for production
npm run lint:css     # Lint CSS files
npm run format:css   # Format CSS files
npm run validate     # Validate HTML
```

### Code Quality
- **Stylelint**: CSS linting and formatting
- **Prettier**: Code formatting
- **HTML Validate**: HTML validation

## 🎨 Customization

### Custom Properties
Modify design tokens in `src/styles/design-system.css`:

```css
:root {
  --color-primary-600: #your-brand-color;
  --font-family-sans: 'Your-Font', sans-serif;
  --spacing-4: 1rem; /* 16px */
}
```

### Component Variants
Extend existing components:

```css
.btn-custom {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: var(--radius-2xl);
}
```

## 📱 Responsive Design

Mobile-first approach with breakpoints:
- **sm**: 640px and up
- **md**: 768px and up  
- **lg**: 1024px and up

Example responsive utilities:
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  <!-- Responsive grid layout -->
</div>
```

## ♿ Accessibility Features

- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: Semantic HTML and ARIA labels
- **Color Contrast**: WCAG AA compliant contrast ratios
- **Focus Indicators**: Visible focus states
- **Motion Preferences**: Respects reduced motion settings

## 🔒 Security Features

- **Content Security Policy**: XSS protection
- **Secure Headers**: X-Frame-Options, X-Content-Type-Options
- **Input Validation**: Client-side form validation
- **HTTPS Enforcement**: Secure connection requirements

## 📊 Performance

- **CSS Bundle Size**: ~35KB (minified)
- **Custom Properties**: Runtime theming
- **Critical CSS**: Above-the-fold optimization
- **Lazy Loading**: Progressive enhancement

## 🌙 Dark Mode

Automatic dark mode detection:
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-gray-50: #1f2937;
    --color-gray-900: #f9fafb;
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Style Guide
- Use CSS custom properties for theming
- Follow BEM methodology for component naming
- Mobile-first responsive design
- Maintain accessibility standards

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NCUK**: Northern Consortium of UK Universities
- **Design Inspiration**: Modern design system principles
- **Accessibility**: WCAG 2.1 guidelines
- **Performance**: Web Core Vitals optimization

---

**Built with ❤️ for NCUK by the development team**