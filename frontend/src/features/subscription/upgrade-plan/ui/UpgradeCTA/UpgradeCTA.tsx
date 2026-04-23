import { Crown } from 'lucide-react';
import { Button } from '../../../../../shared/ui/button/Button';
import { useMockPurchase } from '../../../mock-purchase';

interface UpgradeCTAProps {
  planId: number;
  disabled?: boolean;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary' | 'ghost';
}

export function UpgradeCTA({
  planId,
  disabled = false,
  label = 'Upgrade',
  size = 'md',
  variant = 'primary',
}: UpgradeCTAProps) {
  const { purchase, mutation } = useMockPurchase();

  return (
    <Button
      type="button"
      size={size}
      variant={variant}
      disabled={disabled}
      isLoading={mutation.isPending}
      leftIcon={<Crown size={16} />}
      onClick={() => purchase(planId)}
    >
      {label}
    </Button>
  );
}
