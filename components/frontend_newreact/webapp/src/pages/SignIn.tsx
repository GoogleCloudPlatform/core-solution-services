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
    <div className="min-h-screen px-4 md:px-10">
      <div className="flex min-h-screen max-w-6xl items-center justify-center">
        <div className="mx-auto w-3/4 text-center md:w-1/2">
          <div className="flex items-center justify-center">
            <img
              className="h-20 w-auto pr-6"
              src={AppConfig.logoPath}
              alt={t("app.title")}
            />
            <div className="text-center text-xl font-semibold">
              {t("app.title")}
            </div>
          </div>

          <div className="mb-16 mt-4">{t("app.description")}</div>

          <div className="sm:px-20 md:px-10 lg:px-0 xl:px-20">
            <SignInForm authOptions={AppConfig.authProviders} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default SignIn;