import { createContext, useContext, useEffect, useState } from 'react'
import { User } from '../../src/lib/types'
import { auth } from '../../src/lib/firebase'

interface AuthContextType {
  user: User | null;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({ user: null, loading: true });

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (firebaseUser) => {
      if (firebaseUser) {
        try {
          // Get the ID token
          const token = await firebaseUser.getIdToken();
          // Create extended user object with token
          const userWithToken = {
            ...firebaseUser,
            token,
            firstName: '', // Add default values for required User fields
            lastName: ''
          } as User;
          setUser(userWithToken);
        } catch (error) {
          console.error('Error getting auth token:', error);
          setUser(null);
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    // Set up token refresh
    const tokenRefreshInterval = setInterval(async () => {
      if (auth.currentUser) {
        try {
          const token = await auth.currentUser.getIdToken(true);
          setUser(prev => prev ? { ...prev, token } as User : null);
        } catch (error) {
          console.error('Error refreshing token:', error);
        }
      }
    }, 45 * 60 * 1000); // Refresh token every 45 minutes

    return () => {
      unsubscribe();
      clearInterval(tokenRefreshInterval);
    };
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext); 