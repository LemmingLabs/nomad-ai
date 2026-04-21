import { z } from 'zod';

export const generateTripSchema = z.object({
  budget: z.enum(['low', 'medium', 'high'], {
    error: 'Choose a budget: low, medium, or high',
  }),
  days: z.number().int().min(1).max(14),
  interests: z
    .string()
    .min(2, 'Add at least one interest')
    .refine(
      (value) => value.split(',').map((item) => item.trim()).filter(Boolean).length > 0,
      'Add at least one interest',
    ),
  travel_style: z.string().min(2, 'Enter a travel style'),
  prompt: z.string().max(1000, 'Prompt must be 1000 characters or fewer').optional(),
});

export type GenerateTripFormData = z.infer<typeof generateTripSchema>;
