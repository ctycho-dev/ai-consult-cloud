import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { IGlobalFileRequest, IFile } from "@/interfaces/file";

export const fileApi = createApi({
	reducerPath: 'fileApi',
	baseQuery: fetchBaseQuery({
		baseUrl: `/api/v1/file`,
		// credentials: "include"
	}),
	tagTypes: ['File'],
	endpoints: (builder) => ({
		getFiles: builder.query<IFile[], void>({
			query: () => ({
				url: '/',
				method: 'GET'
			}),
			providesTags: ['File']
		}),

		getFile: builder.query<IFile, number>({
			query: (fileId: number) => `/${fileId}`,
		}),
		uploadFile: builder.mutation<IFile, IGlobalFileRequest>({
			query({ ...rest }) {
				const { files } = rest
				const formData = new FormData();
				formData.append('files', files)
				// files.map((file) => formData.append('files', file));
				// formData.append('company_id', company_id)

				return {
					url: `/upload`,
					method: 'POST',
					body: formData
				}
			},
			invalidatesTags: ['File']
		}),
		// Updated API with proper blob handling
		downloadFile: builder.mutation<void, number>({ // Return void instead of Blob
			query: (fileId: number) => ({
				url: `/${fileId}/download`,
				method: 'GET',
				responseHandler: async (response) => {
					if (!response.ok) {
						throw new Error(`Download failed: ${response.statusText}`);
					}
					return response.blob();
				},
			}),
			transformResponse: async (blob: Blob, meta, fileId) => {
				let filename = `file_${fileId}`;

				// Try different ways to access headers based on RTK Query version
				let contentDisposition = null;

				if (meta?.baseQueryMeta?.response?.headers) {
					contentDisposition = meta.baseQueryMeta.response.headers.get('Content-Disposition');
				} else if (meta?.response?.headers) {
					contentDisposition = meta.response.headers.get('Content-Disposition');
				}

				console.log('Content-Disposition header:', contentDisposition); // Debug

				if (contentDisposition) {
					// Parse the header that matches your backend format
					// Format: attachment; filename="ascii_name"; filename*=UTF-8''encoded_name

					// Try RFC 5987 encoded filename first (better Unicode support)
					const encodedMatch = contentDisposition.match(/filename\*=UTF-8''([^;\s]+)/);
					if (encodedMatch) {
						try {
							filename = decodeURIComponent(encodedMatch[1]);
							console.log('Using RFC 5987 filename:', filename);
						} catch (e) {
							console.warn('Failed to decode RFC 5987 filename:', e);
						}
					} else {
						// Fallback to regular quoted filename
						const quotedMatch = contentDisposition.match(/filename="([^"]+)"/);
						if (quotedMatch) {
							filename = quotedMatch[1];
							console.log('Using quoted filename:', filename);
						}
					}
				}

				const url = window.URL.createObjectURL(blob);
				const link = document.createElement('a');
				link.href = url;
				link.download = filename;
				document.body.appendChild(link);
				link.click();

				// Cleanup
				document.body.removeChild(link);
				window.URL.revokeObjectURL(url);

				return undefined;
			},
			// Don't cache file downloads
			transformErrorResponse: (response) => response.data,
		}),


		deleteFile: builder.mutation<void | IFile, number>({
			query: (fileId) => ({
				url: `/${fileId}`,
				method: "DELETE",
			}),
			invalidatesTags: ['File']
		}),
	})
});

export const {
	useGetFilesQuery,
	useGetFileQuery,
	useDownloadFileMutation,
	useUploadFileMutation,
	useDeleteFileMutation
} = fileApi;