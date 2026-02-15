function createNav() {
  const isLoggedIn = localStorage.getItem('logged_in') === 'true';
  const currentTheme = localStorage.getItem('theme') || 'dark';
  
  const nav = document.createElement('nav');
  
  // Home button
  const homeBtn = document.createElement('a');
  homeBtn.href = '/';
  homeBtn.textContent = '🏠 Home';
  nav.appendChild(homeBtn);
  
  // Account button (only if logged in)
  if (isLoggedIn) {
    const accountBtn = document.createElement('a');
    accountBtn.href = '/account';
    accountBtn.textContent = '👤 Account';
    nav.appendChild(accountBtn);
  }
  
  // About button
  const aboutBtn = document.createElement('a');
  aboutBtn.href = '/about';
  aboutBtn.textContent = 'ℹ️ About';
  nav.appendChild(aboutBtn);
  
  // Contact button
  const contactBtn = document.createElement('a');
  contactBtn.href = '/contact';
  contactBtn.textContent = '✉️ Contact Us';
  nav.appendChild(contactBtn);
  
  // Spacer
  const spacer = document.createElement('div');
  spacer.className = 'nav-spacer';
  nav.appendChild(spacer);
  
  // Theme toggle button
  const themeBtn = document.createElement('button');
  themeBtn.textContent = currentTheme === 'dark' ? '☀️ Light' : '🌙 Dark';
  themeBtn.onclick = (e) => {
    e.preventDefault();
    const isLight = document.body.classList.contains('light-theme');
    const newTheme = isLight ? 'dark' : 'light';
    localStorage.setItem('theme', newTheme);
    document.body.classList.toggle('light-theme');
    themeBtn.textContent = newTheme === 'dark' ? '☀️ Light' : '🌙 Dark';
    
    // Save theme to server if logged in
    if (isLoggedIn) {
      fetch('/api/account/update-theme', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ theme: newTheme })
      }).catch(err => console.error('Theme save error:', err));
    }
  };
  nav.appendChild(themeBtn);
  
  // Back button (except on home)
  if (window.location.pathname !== '/' && window.location.pathname !== '/index.html') {
    const backBtn = document.createElement('button');
    backBtn.textContent = '← Back';
    backBtn.style.marginLeft = '12px';
    backBtn.onclick = (e) => {
      e.preventDefault();
      window.history.back();
    };
    nav.appendChild(backBtn);
  }
  
  return nav;
}

document.addEventListener('DOMContentLoaded', () => {
  // Apply saved theme
  const savedTheme = localStorage.getItem('theme') || 'dark';
  if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
  }
  
  // Insert nav at the start of main content
  const main = document.querySelector('main');
  if (main && !document.querySelector('nav')) {
    main.insertBefore(createNav(), main.firstChild);
  }
  
  // Update logged in status from session
  fetch('/api/account/info')
    .then(r => r.json())
    .then(data => {
      if (data.user) {
        localStorage.setItem('logged_in', 'true');
      } else {
        localStorage.setItem('logged_in', 'false');
      }
    })
    .catch(() => localStorage.setItem('logged_in', 'false'));
});
