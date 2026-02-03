import type FileInfo from '@/model/fileInfo'


export async function uploadFile(
  profileId: string,
  file: File
): Promise<void> {  
  await uploadToStorage(profileId, file);
  await embedDocument(profileId, file);
}


export async function fetchFilesForProfile(
  profileId: string
): Promise<FileInfo[]> {
  try {
    const storedResponse = await fetch(
      `/api/database/${profileId}/documents-stored`
    );

    if (!storedResponse.ok) {
      throw new Error(
        `Failed to fetch stored documents: ${storedResponse.statusText}`
      );
    }

    const storedDocuments = await storedResponse.json();

    const documents: FileInfo[] = storedDocuments.map(
      (doc: any) => ({
        filename: doc.filename,
        blobId: doc.id,
        embeddingsId: '',
      })
    );

    for (const doc of documents) {
      try {
        const embeddedResponse = await fetch(
          `/api/database/documents-embedded?filename=${encodeURIComponent(
            doc.filename
          )}`
        );

        if (embeddedResponse.ok) {
          const embeddedDoc = await embeddedResponse.json();
          doc.embeddingsId = embeddedDoc.id;
        }
      } catch (error) {
        console.warn(`Failed to fetch embedded info for ${doc.filename}`);
      }
    }

    return documents;
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : 'Failed to fetch documents';
    throw new Error(errorMessage);
  }
}


async function uploadToStorage(
  profileId: string,
  file: File
): Promise<void> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(
    `/api/storage/collections/${profileId}/blobs`,
    {
      method: 'POST',
      body: formData,
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(
      `Failed to upload file to storage: ${error.detail || response.statusText}`
    );
  }
}


async function embedDocument(
  profileId: string,
  file: File
): Promise<void> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(
    `/api/embeddings/collections/${profileId}/upload`,
    {
      method: 'POST',
      body: formData,
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(
      `Failed to embed document: ${error.detail || response.statusText}`
    );
  }
}


export async function downloadFile(
  profileId: string,
  filename: string
): Promise<void> {
  const response = await fetch(
    `/api/storage/collections/${profileId}/blobs/${encodeURIComponent(
      filename
    )}`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to download file: ${response.statusText}`
    );
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}


export async function downloadEmbeddings(
  filename: string
): Promise<void> {
  const response = await fetch(
    `/api/database/documents-embedded?filename=${encodeURIComponent(
      filename
    )}`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch embeddings: ${response.statusText}`
    );
  }

  const embeddedDoc = await response.json();

  const embeddings = typeof embeddedDoc.points === 'string'
    ? JSON.parse(embeddedDoc.points)
    : embeddedDoc.points;

  const jsonString = JSON.stringify(embeddings, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename.replace(/\.[^/.]+$/, '')}_embeddings.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}


export async function deleteFile(
  profileId: string,
  filename: string
): Promise<void> {
  const response = await fetch(
    `/api/storage/collections/${profileId}/blobs/${encodeURIComponent(
      filename
    )}`,
    {
      method: 'DELETE',
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(
      `Failed to delete file: ${error.detail || response.statusText}`
    );
  }

  try {
    await fetch(
      `/api/embeddings/collections/${profileId}/documents/${encodeURIComponent(
        filename
      )}`,
      {
        method: 'DELETE',
      }
    );
  } catch (error) {
    console.warn(
      `Failed to delete embeddings for ${filename}:`,
      error
    );
  }
}
