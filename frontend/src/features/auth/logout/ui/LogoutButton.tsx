import { LogOut } from 'lucide-react';
import cn from 'classnames';
import { useLogout } from '../model/useLogout';
import styles from './LogoutButton.module.scss';

interface LogoutButtonProps {
  isCollapsed?: boolean;
}

export function LogoutButton({ isCollapsed = false }: LogoutButtonProps) {
  const logoutMutation = useLogout();

  return (
    <button
      type="button"
      className={cn(styles.button, {
        [styles['button--collapsed']]: isCollapsed,
      })}
      onClick={() => logoutMutation.mutate()}
      disabled={logoutMutation.isPending}
      aria-label="Log out"
      title="Log out"
    >
      <LogOut size={16} />
      {!isCollapsed && <span>{logoutMutation.isPending ? 'Logging out...' : 'Log out'}</span>}
    </button>
  );
}
