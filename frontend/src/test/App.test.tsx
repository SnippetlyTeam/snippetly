import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    // Check that the app renders (basic smoke test)
    expect(document.body).toBeTruthy();
  });

  it('contains main application structure', () => {
    const { container } = render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    // Verify the app has rendered some content
    expect(container.firstChild).toBeTruthy();
  });
});
