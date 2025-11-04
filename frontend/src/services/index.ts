// Export all services from a central location
export * from './authService';
export * from './productService';
export * from './orderService';
export * from './customerService';

// Re-export the main API instance
export { default as api } from '@/lib/api';
