import { PDFDocument } from 'pdf-lib'


const MAX_FILE_SIZE_MB = 50


export interface SplitPart {
  file: File
  pageStart: number
  pageEnd: number
  totalPages: number
}


export function getMaxFileSizeMb(): number {
  return MAX_FILE_SIZE_MB
}


export function getMaxFileSizeBytes(): number {
  return MAX_FILE_SIZE_MB * 1024 * 1024
}


export function fileSizeExceedsMax(file: File): boolean {
  return file.size > getMaxFileSizeBytes()
}


export function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}


export async function getPageCount(file: File): Promise<number> {
  const arrayBuffer = await file.arrayBuffer()
  const pdfDoc = await PDFDocument.load(arrayBuffer)
  return pdfDoc.getPageCount()
}


export async function splitPdf(
  file: File,
  pagesPerPart: number
): Promise<SplitPart[]> {
  const arrayBuffer = await file.arrayBuffer()
  const sourcePdf = await PDFDocument.load(arrayBuffer)
  const totalPages = sourcePdf.getPageCount()

  const parts: SplitPart[] = []
  const baseName = file.name.replace(/\.pdf$/i, '')

  for (
    let startPage = 0;
    startPage < totalPages;
    startPage += pagesPerPart
  ) {
    const endPage = Math.min(
      startPage + pagesPerPart,
      totalPages
    )

    const newPdf = await PDFDocument.create()
    const pageIndices = Array.from(
      { length: endPage - startPage },
      (_, i) => startPage + i
    )
    const copiedPages = await newPdf.copyPages(
      sourcePdf,
      pageIndices
    )

    for (const page of copiedPages) {
      newPdf.addPage(page)
    }

    const pdfBytes = await newPdf.save()
    const partNumber = Math.floor(startPage / pagesPerPart) + 1
    const partFilename = `${baseName}_part${partNumber}.pdf`

    const partFile = new File(
      [pdfBytes],
      partFilename,
      { type: 'application/pdf' }
    )

    parts.push({
      file: partFile,
      pageStart: startPage + 1,
      pageEnd: endPage,
      totalPages: totalPages,
    })
  }

  return parts
}
