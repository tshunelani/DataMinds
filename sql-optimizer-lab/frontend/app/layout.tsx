import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SQL Optimizer Lab',
  description: 'Iterative SQL optimization and benchmark workbench',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
