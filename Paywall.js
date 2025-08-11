// /components/Paywall.js - Your exact component, enhanced
import { loadStripe } from '@stripe/stripe-js';

const Paywall = () => {
  const handleClick = async () => {
    try {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });
      
      const { id, error } = await res.json();
      
      if (error) {
        console.error('Checkout error:', error);
        return;
      }
      
      const stripe = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_KEY);
      await stripe.redirectToCheckout({ sessionId: id });
      
    } catch (error) {
      console.error('Payment failed:', error);
    }
  };

  return (
    <button 
      onClick={handleClick}
      style={{
        backgroundColor: '#4F46E5',
        color: 'white',
        padding: '15px 30px',
        border: 'none',
        borderRadius: '8px',
        fontSize: '16px',
        fontWeight: 'bold',
        cursor: 'pointer'
      }}
    >
      Buy Credits ($9.99)
    </button>
  );
};

export default Paywall;