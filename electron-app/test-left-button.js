// Test script for debugging left titlebar button
// Paste this in DevTools Console (Cmd+Option+I)

console.log('=== LEFT SIDEBAR BUTTON TEST ===\n');

// Find elements
const leftBtn = document.getElementById('titlebar-toggle-left');
const layout = document.querySelector('.three-column-layout');

console.log('1. Button exists:', !!leftBtn);
console.log('2. Layout exists:', !!layout);

if (leftBtn) {
  console.log('3. Button computed styles:');
  const styles = window.getComputedStyle(leftBtn);
  console.log('   - position:', styles.position);
  console.log('   - z-index:', styles.zIndex);
  console.log('   - pointer-events:', styles.pointerEvents);
  console.log('   - display:', styles.display);
  console.log('   - width x height:', styles.width, 'x', styles.height);
  
  console.log('4. Button location in DOM:');
  console.log('   - parent:', leftBtn.parentElement?.className);
  console.log('   - offsetLeft:', leftBtn.offsetLeft);
  console.log('   - offsetTop:', leftBtn.offsetTop);
  
  console.log('5. Current sidebar state:');
  console.log('   - left-collapsed:', layout?.classList.contains('left-collapsed'));
  console.log('   - right-collapsed:', layout?.classList.contains('right-collapsed'));
  
  console.log('\n6. Testing manual click...');
  leftBtn.click();
  
  setTimeout(() => {
    console.log('7. Sidebar state AFTER manual click:');
    console.log('   - left-collapsed:', layout?.classList.contains('left-collapsed'));
    console.log('\n=== TEST COMPLETE ===');
    console.log('Check above for [CLICK EVENT] and [DEBUG] messages');
  }, 100);
} else {
  console.error('Button not found!');
}
