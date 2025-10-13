# Ramon ADN - Oligo Toolkit Frontend

A modern React application for DNA sequence analysis and oligo generation.

## 🏗️ Architecture

The application follows a modular, component-based architecture:

```
src/
├── components/          # Reusable components
│   ├── common/         # Common components (Header, Layout, Button)
│   └── ui/             # UI-specific components (Card, Modal, Form)
├── pages/              # Page components
│   ├── Dashboard/      # Main dashboard
│   ├── OligoMaker/     # Oligo generation
│   └── Mutagenesis/    # Mutagenesis tools
├── services/           # API services
├── utils/              # Utility functions
├── hooks/              # Custom React hooks
├── context/            # React context providers
└── styles/             # Global styles and variables
```

## 🚀 Features

- **Oligo Generation**: Generate forward and reverse oligos from DNA sequences
- **Mutagenesis Tools**: Saturation, custom, and scanning mutagenesis
- **Sequence Analysis**: Analyze DNA sequence properties (GC%, Tm, etc.)
- **Modern UI**: Clean, responsive interface with dark/light theme support
- **Error Handling**: Robust error handling and validation
- **Type Safety**: Comprehensive input validation and sanitization

## 🛠️ Technology Stack

- **React 19**: Latest React features with concurrent rendering
- **CSS Custom Properties**: Modern CSS with theming support
- **Context API**: Global state management
- **Custom Hooks**: Reusable logic for API calls
- **Modern JavaScript**: ES2022+ features

## 📦 Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API URL and settings
   ```

3. **Start development server**:
   ```bash
   npm start
   ```

4. **Build for production**:
   ```bash
   npm run build
   ```

## 🔧 Configuration

### Environment Variables

- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_DEFAULT_THEME`: Default theme (light/dark)
- `REACT_APP_ENABLE_DARK_MODE`: Enable theme switching

### API Integration

The app communicates with the backend API through service modules:

- `services/api.js`: Base API client
- `services/oligos.js`: Oligo generation endpoints
- `services/mutagenesis.js`: Mutagenesis endpoints

## 🎨 Theming

The application supports light and dark themes using CSS custom properties:

```css
:root {
  --color-primary: #007bff;
  --bg-primary: #ffffff;
  --text-primary: #212529;
}

[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --text-primary: #ffffff;
}
```

## 🧩 Component Usage

### Basic Components

```jsx
import Button from 'components/common/Button/Button';
import Card from 'components/ui/Card/Card';

<Button variant="primary" loading={isLoading} onClick={handleClick}>
  Generate Oligos
</Button>

<Card title="Results" hoverable>
  <p>Your oligo results...</p>
</Card>
```

### API Hooks

```jsx
import useApi from 'hooks/useApi';
import oligoService from 'services/oligos';

const { loading, error, execute } = useApi();

const generateOligos = async () => {
  try {
    const result = await execute(oligoService.generateOligos, params);
    // Handle success
  } catch (err) {
    // Error handled by hook
  }
};
```

## 📱 Responsive Design

The application is fully responsive with breakpoints:

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 🔍 Code Quality

- **Consistent Structure**: Each component has its own folder with JS and CSS
- **Naming Convention**: BEM methodology for CSS classes
- **Error Boundaries**: Graceful error handling
- **Accessibility**: ARIA labels and semantic HTML

## 🚦 Development Guidelines

### Component Structure

```
ComponentName/
├── ComponentName.js    # Component logic
├── ComponentName.css   # Component styles
└── index.js           # Export file (optional)
```

### Styling Guidelines

- Use CSS custom properties for theming
- Follow BEM naming convention
- Keep component styles scoped
- Use utility classes for common patterns

### State Management

- Use React Context for global state
- Custom hooks for reusable logic
- Local state for component-specific data

## 🔄 Migration Notes

This new structure provides:

- Better code organization
- Improved maintainability
- Enhanced reusability
- Modern development practices
- Consistent styling system
- Robust error handling

## 📋 TODO

- [ ] Migrate remaining components
- [ ] Add comprehensive tests
- [ ] Implement advanced error boundaries
- [ ] Add internationalization support
- [ ] Optimize bundle size
- [ ] Add Progressive Web App features