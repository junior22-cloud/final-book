// HOTFIX: Replace the selectTier function in deployed index.html
// This works with your current JSON-returning backend

function selectTier(tier) {
  selectedTier = tier;
  
  // Get the topic
  const topic = document.getElementById('selectedTopic').textContent;
  if (!topic || topic === '') {
    alert('Please enter a book topic first!');
    return;
  }
  
  // Clear previous selections
  document.querySelectorAll('.pricing-card').forEach(card => {
    card.classList.remove('selected');
  });
  
  // Select current tier
  event.currentTarget.classList.add('selected');
  
  // Show loading state
  const loadingMsg = document.createElement('div');
  loadingMsg.id = 'checkout-loading';
  loadingMsg.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:20px;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.3);z-index:9999;';
  loadingMsg.innerHTML = `<h3>🚀 Processing ${tier.toUpperCase()} package...</h3><p>Redirecting to checkout...</p>`;
  document.body.appendChild(loadingMsg);
  
  // Call your current backend API
  fetch(`/api/checkout?topic=${encodeURIComponent(topic)}&tier=${tier}`)
    .then(response => response.json())
    .then(data => {
      // Remove loading message
      const loading = document.getElementById('checkout-loading');
      if (loading) loading.remove();
      
      if (data.checkout_url) {
        // Redirect to Stripe checkout URL
        window.location.href = data.checkout_url;
      } else if (data.demo) {
        // Demo mode - show demo checkout
        alert(`DEMO MODE: ${tier.toUpperCase()} - $${data.price}\n\nIn production, this would redirect to Stripe checkout.\n\nAdd your STRIPE_SECRET_KEY to Railway environment variables to enable real payments.`);
      } else {
        throw new Error('No checkout URL received');
      }
    })
    .catch(error => {
      // Remove loading message
      const loading = document.getElementById('checkout-loading');
      if (loading) loading.remove();
      
      console.error('Checkout error:', error);
      alert('Sorry, checkout failed. Please try again.');
    });
}

// INSTRUCTIONS:
// 1. Copy this function
// 2. Go to Railway deployed version
// 3. Replace the existing selectTier function with this one
// 4. Your buttons will work immediately!