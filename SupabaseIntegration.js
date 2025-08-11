// Supabase Integration for BookWiz (Optional Enhancement)
import React, { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_KEY;

// Initialize Supabase client (only if environment variables are present)
export const supabase = supabaseUrl && supabaseKey ? 
  createClient(supabaseUrl, supabaseKey) : null;

// User Authentication Hook
export const useSupabaseAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!supabase) {
      setLoading(false);
      return;
    }

    // Get initial session
    const getInitialSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user ?? null);
      setLoading(false);
    };

    getInitialSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setUser(session?.user ?? null);
        setLoading(false);
      }
    );

    return () => subscription?.unsubscribe();
  }, []);

  const signUp = async (email, password) => {
    if (!supabase) return { error: 'Supabase not configured' };
    
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    });

    return { data, error };
  };

  const signIn = async (email, password) => {
    if (!supabase) return { error: 'Supabase not configured' };
    
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    return { data, error };
  };

  const signOut = async () => {
    if (!supabase) return;
    await supabase.auth.signOut();
  };

  return { user, loading, signUp, signIn, signOut };
};

// Book Storage Service
export const BookService = {
  // Save generated book to Supabase
  async saveBook(userId, bookData) {
    if (!supabase) return { error: 'Supabase not configured' };

    const { data, error } = await supabase
      .from('books')
      .insert({
        user_id: userId,
        title: bookData.title,
        content: bookData.content,
        prompt: bookData.prompt,
        word_count: bookData.wordCount,
        created_at: new Date().toISOString()
      });

    return { data, error };
  },

  // Get user's books
  async getUserBooks(userId) {
    if (!supabase) return { error: 'Supabase not configured' };

    const { data, error } = await supabase
      .from('books')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    return { data, error };
  },

  // Delete a book
  async deleteBook(bookId) {
    if (!supabase) return { error: 'Supabase not configured' };

    const { error } = await supabase
      .from('books')
      .delete()
      .eq('id', bookId);

    return { error };
  }
};

// Enhanced BookWiz with Supabase
export const BookWizWithAuth = () => {
  const { user, loading, signUp, signIn, signOut } = useSupabaseAuth();
  const [books, setBooks] = useState([]);

  // Load user's books when authenticated
  useEffect(() => {
    if (user && supabase) {
      loadUserBooks();
    }
  }, [user]);

  const loadUserBooks = async () => {
    const { data, error } = await BookService.getUserBooks(user.id);
    if (!error && data) {
      setBooks(data);
    }
  };

  const saveGeneratedBook = async (bookData) => {
    if (!user) return;
    
    const { error } = await BookService.saveBook(user.id, bookData);
    if (!error) {
      loadUserBooks(); // Refresh the list
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Sign in to BookWiz</h2>
        <p>Save and manage your generated books</p>
        {/* Add your auth forms here */}
      </div>
    );
  }

  return (
    <div>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        padding: '10px',
        borderBottom: '1px solid #eee'
      }}>
        <span>Welcome, {user.email}</span>
        <button onClick={signOut}>Sign Out</button>
      </div>
      
      {/* Your existing BookWiz component */}
      <BookWizGenerator onBookGenerated={saveGeneratedBook} />
      
      {/* User's saved books */}
      <div style={{ marginTop: '30px' }}>
        <h3>Your Generated Books ({books.length})</h3>
        {books.map(book => (
          <div key={book.id} style={{ 
            padding: '15px', 
            border: '1px solid #ddd', 
            margin: '10px 0',
            borderRadius: '5px'
          }}>
            <h4>{book.title}</h4>
            <p>Generated: {new Date(book.created_at).toLocaleDateString()}</p>
            <p>Words: {book.word_count}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

// SQL for Supabase (create this table in your Supabase dashboard)
/*
CREATE TABLE books (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  prompt TEXT,
  word_count INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE books ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only see their own books" ON books
  FOR ALL USING (auth.uid() = user_id);
*/