import styles from './ProfilePage.module.scss';
import Snippet from '../../components/Snippet/Snippet';
import { useQuery } from '@tanstack/react-query';
import { getAll } from '../../api/snippetsClient';
import { Loader } from '../../components/Loader';
import { useAuthContext } from '../../contexts/AuthContext';
import { useOutletContext, useLocation, useNavigate } from 'react-router-dom';
import type { ProfileType } from '../../types/ProfileType';
import Pagination from '../../components/Pagination/Pagination';
import type { SnippetType } from '../../types/SnippetType';

const Snippets = () => {
  const { accessToken } = useAuthContext();
  const { profile } = useOutletContext<{ profile: ProfileType }>();
  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const currentPage = parseInt(params.get('page') || '1', 10);

  const { data, isPending, isSuccess } = useQuery({
    queryKey: ['profileSnippets', profile.username, accessToken, currentPage],
    queryFn: () => getAll(accessToken, { username: profile.username, page: currentPage }),
    enabled: !!accessToken && !!profile.username,
  });

  function handlePageChange(_: any, value: number) {
    const params = new URLSearchParams(location.search);

    if (value && value >= 1) {
      if (value !== 1) {
        params.set('page', String(value));
      } else {
        params.delete('page');
      }
    } else {
      params.delete('page');
    }

    navigate({ search: params.toString() ? `?${params.toString()}` : '' });
  }

  return (
    <div className={styles.snippets}>
      {isPending ? (
        <Loader />
      ) : !isSuccess ? (
        <div>
          <strong>Oops! We couldn't load the snippets.</strong>
          <br />
          Please check your connection or try refreshing the page.
        </div>
      ) : data?.data?.snippets?.length === 0 ? (
        <div>
          You haven't shared any code snippets yet.<br />Start by creating and sharing your awesome code!
        </div>
      ) : (
        <>
          <div className={styles.snippetsList}>
            {data.data.snippets.map((item: SnippetType) => (
              <Snippet key={item.uuid} snippet={item} />
            ))}
          </div>

          <Pagination
            totalPages={data.data.total_pages || 1}
            currentPage={data.data.page || 1}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </div>
  );
};

export default Snippets;