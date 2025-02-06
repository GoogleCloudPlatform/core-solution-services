import SignInForm from '@/components/SignInForm';
import { AppConfig } from '@/lib/auth';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from "react-i18next"
import { useAuth } from '@/contexts/AuthContext';
import { useEffect } from 'react';

const SignIn = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { t } = useTranslation()

  useEffect(() => {
    if (user) {
      navigate('/');
    }
  }, [user, navigate]);

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
            <div className="text-xl font-semibold text-black">
              {t("app.title")}
            </div>
          </div>

          <div className="mt-4 mb-8 text-black">{t("app.description")}</div>

          <div className="w-full">
            <SignInForm authOptions={AppConfig.authProviders} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default SignIn;