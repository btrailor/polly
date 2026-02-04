// Paste this in DevTools Console to check if CSS changes are applied

console.log('=== Titlebar Button Style Check ===');

const leftBtn = document.getElementById('titlebar-toggle-left');
const rightBtn = document.getElementById('titlebar-toggle-right');

if (leftBtn) {
  const styles = window.getComputedStyle(leftBtn);
  console.log('Left Button Styles:');
  console.log('  width:', styles.width, '(should be 24px)');
  console.log('  height:', styles.height, '(should be 24px)');
  console.log('  padding:', styles.padding, '(should be 4px)');
  console.log('  border-radius:', styles.borderRadius, '(should be 3px)');
  
  const svg = leftBtn.querySelector('svg');
  if (svg) {
    const svgStyles = window.getComputedStyle(svg);
    console.log('  SVG width:', svgStyles.width, '(should be 14px)');
    console.log('  SVG height:', svgStyles.height, '(should be 14px)');
  }
} else {
  console.error('Left button not found!');
}

const titlebar = document.querySelector('.titlebar');
if (titlebar) {
  const tbStyles = window.getComputedStyle(titlebar);
  console.log('\nTitlebar Styles:');
  console.log('  height:', tbStyles.height, '(should be 40px)');
} else {
  console.error('Titlebar not found!');
}

const layout = document.querySelector('.three-column-layout');
if (layout) {
  console.log('\nLayout State:');
  console.log('  classes:', layout.className);
  console.log('  left collapsed:', layout.classList.contains('left-collapsed'));
  console.log('  right collapsed:', layout.classList.contains('right-collapsed'));
} else {
  console.error('Three column layout not found!');
}

console.log('\n=== localStorage State ===');
console.log('  sidebar-left-collapsed:', localStorage.getItem('sidebar-left-collapsed'));
console.log('  sidebar-right-collapsed:', localStorage.getItem('sidebar-right-collapsed'));
