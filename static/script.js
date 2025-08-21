// Frontend JavaScript for WizBook Generator
const API_BASE_URL = window.location.origin;

async function startCheckout(tier) {
    try {
        // Show loading state
        document.getElementById('loading').classList.remove('hidden');
        
        const response = await fetch(`${API_BASE_URL}/api/create-checkout-session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer your-frontend-api-key' // Change this!
            },
            body: JSON.stringify({ 
                tier: tier,
                topic: "AI-Generated Book" // You can add a prompt input later
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Checkout failed');
        }

        const data = await response.json();
        
        // Redirect to Stripe Checkout
        window.location.href = data.checkout_url;
        
    } catch (error) {
        console.error('Checkout error:', error);
        alert('Error starting checkout: ' + error.message);
        document.getElementById('loading').classList.add('hidden');
    }
}

// Handle success page
if (window.location.pathname === '/success') {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if (sessionId) {
        document.body.innerHTML = `
            <div class="container">
                <div style="text-align: center; color: white;">
                    <h2>Payment Successful! 🎉</h2>
                    <p>Your WizBook is being generated. You'll receive an email shortly.</p>
                    <p>Session ID: ${sessionId}</p>
                    <a href="/" style="color: #fff; text-decoration: underline;">Return Home</a>
                </div>
            </div>
        `;
    }
}

// Handle cancel page
if (window.location.pathname === '/cancel') {
    document.body.innerHTML = `
        <div class="container">
            <div style="text-align: center; color: white;">
                <h2>Payment Cancelled</h2>
                <p>Your payment was cancelled. No charges were made.</p>
                <a href="/" style="color: #fff; text-decoration: underline;">Return Home</a>
            </div>
        </div>
    `;
}
