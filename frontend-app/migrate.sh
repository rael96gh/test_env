#!/bin/bash

# Ramon ADN Frontend Migration Script
echo "🚀 Starting frontend migration to new architecture..."

# Create backup
echo "📦 Creating backup of current files..."
mkdir -p backup
cp src/App.js backup/App.js.backup
cp src/index.js backup/index.js.backup
cp src/App.css backup/App.css.backup
cp src/index.css backup/index.css.backup

# Replace main files
echo "🔄 Updating main application files..."
mv src/App_new.js src/App.js
mv src/index_new.js src/index.js

# Update index.css to import global styles
echo "🎨 Updating global styles..."
cat > src/index.css << 'EOF'
/* Global styles - now using new architecture */
@import './styles/globals.css';

/* Legacy compatibility styles */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
EOF

# Clean up old styles
echo "🧹 Cleaning up old styles..."
if [ -f "recycling_tool.css" ]; then
    mv recycling_tool.css backup/recycling_tool.css.backup
fi

# Update gitignore
echo "📝 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# New architecture files
/src/components/
/src/pages/
/src/services/
/src/utils/
/src/hooks/
/src/context/
/src/styles/
backup/
*.backup
EOF

# Move README
mv README_new.md README.md

echo "✅ Migration completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Review the new structure in src/"
echo "2. Test the application: npm start"
echo "3. Migrate remaining components gradually"
echo "4. Update API endpoints to use new services"
echo ""
echo "📁 Backup files available in backup/ directory"
echo "📖 Check README.md for detailed documentation"