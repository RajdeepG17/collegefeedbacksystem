import * as Yup from 'yup';

export const feedbackSchema = Yup.object().shape({
    title: Yup.string()
        .required('Title is required')
        .min(5, 'Title must be at least 5 characters')
        .max(200, 'Title must not exceed 200 characters'),
    
    description: Yup.string()
        .required('Description is required')
        .min(10, 'Description must be at least 10 characters')
        .max(2000, 'Description must not exceed 2000 characters'),
    
    category: Yup.string()
        .required('Category is required'),
    
    priority: Yup.string()
        .required('Priority is required')
        .oneOf(['low', 'medium', 'high', 'urgent'], 'Invalid priority level'),
    
    is_anonymous: Yup.boolean(),
    
    attachment: Yup.mixed()
        .test('fileSize', 'File size must be less than 10MB', (value) => {
            if (!value) return true;
            return value.size <= 10 * 1024 * 1024;
        })
        .test('fileType', 'Only image files are allowed (jpg, jpeg, png, gif)', (value) => {
            if (!value) return true;
            const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
            return allowedTypes.includes(value.type);
        }),
});

export const commentSchema = Yup.object().shape({
    comment: Yup.string()
        .required('Comment is required')
        .min(1, 'Comment must be at least 1 character')
        .max(1000, 'Comment must not exceed 1000 characters'),
    
    is_internal: Yup.boolean(),
    
    attachment: Yup.mixed()
        .test('fileSize', 'File size must be less than 10MB', (value) => {
            if (!value) return true;
            return value.size <= 10 * 1024 * 1024;
        })
        .test('fileType', 'Only image files are allowed (jpg, jpeg, png, gif)', (value) => {
            if (!value) return true;
            const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
            return allowedTypes.includes(value.type);
        }),
});

export const ratingSchema = Yup.object().shape({
    rating: Yup.number()
        .required('Rating is required')
        .min(1, 'Rating must be at least 1')
        .max(5, 'Rating must not exceed 5'),
    
    comment: Yup.string()
        .max(500, 'Comment must not exceed 500 characters'),
}); 