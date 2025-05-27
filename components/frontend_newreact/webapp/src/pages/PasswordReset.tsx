import { useState } from 'react';
import { auth } from '../../src/lib/firebase';
import { sendPasswordResetEmail } from 'firebase/auth';
import { AppConfig } from '../../src/lib/auth';
import { useTranslation } from "react-i18next";
import { Link } from 'react-router-dom';

const PasswordReset = () => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const { t } = useTranslation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage(null);

    try {
      await sendPasswordResetEmail(auth, email);
      setMessage({
        type: 'success',
        text: 'Password reset email sent. Please check your inbox.'
      });
      setEmail('');
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.message || 'Failed to send reset email. Please try again.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#1a1a1a]">
      <div className="flex min-h-screen items-center justify-center px-4 md:px-10">
        <div className="w-full max-w-md rounded-lg bg-[#FFFFFF] p-8 shadow-lg">
          <div className="flex flex-col items-center justify-center">
            <img
              className="h-20 w-auto mb-4"
              src={AppConfig.logoPath}
              alt={t("app.title")}
            />
            <div className="text-xl font-semibold text-black mb-4">
              Reset Password
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-black">
                Email address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-black shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Enter your email"
                required
              />
            </div>

            {message && (
              <div className={`p-3 rounded-md ${
                message.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}>
                {message.text}
              </div>
            )}

            <div className="flex items-center justify-between">
              <Link to="/signin" className="text-sm text-blue-600 hover:text-blue-500">
                Back to Sign In
              </Link>
              <button
                type="submit"
                disabled={isSubmitting}
                className={`rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 ${
                  isSubmitting ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {isSubmitting ? 'Sending...' : 'Reset Password'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default PasswordReset; 