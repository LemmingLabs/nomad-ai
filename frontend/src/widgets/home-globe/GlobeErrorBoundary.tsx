import { Component, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  onFailure: () => void;
  fallback: ReactNode;
}

interface State {
  failed: boolean;
}

export class GlobeErrorBoundary extends Component<Props, State> {
  state: State = { failed: false };

  static getDerivedStateFromError(): State {
    return { failed: true };
  }

  componentDidCatch() {
    this.props.onFailure();
  }

  render() {
    return this.state.failed ? this.props.fallback : this.props.children;
  }
}
