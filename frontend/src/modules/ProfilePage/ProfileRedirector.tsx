import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getProfile } from '../../api/profileClient';
import { useAuthContext } from '../../contexts/AuthContext';
import { Loader } from '../../components/Loader';

const ProfileRedirector = () => {
  const { accessToken } = useAuthContext();
  const navigate = useNavigate();

  const { data: profile } = useQuery({
    queryKey: ['myProfileForRedirect'],
    queryFn: () => getProfile(accessToken).then(res => res.data),
    enabled: !!accessToken,
  });

  useEffect(() => {
    if (profile?.username) {
      navigate(`/profile/${profile.username}`, { replace: true });
    }
  }, [profile, navigate]);

  return <Loader />;
};

export default ProfileRedirector;