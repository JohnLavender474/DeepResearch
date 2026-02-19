import {
  nextTick,
  onBeforeUnmount,
  onMounted,
  onUpdated,
  type Ref,
} from 'vue'


const syncScroll = (
  source: HTMLElement,
  target: HTMLElement,
): void => {
  const sourceElement = source as HTMLElement & { syncing?: boolean }
  const targetElement = target as HTMLElement & { syncing?: boolean }

  if (sourceElement.syncing) {
    return
  }

  targetElement.syncing = true
  target.scrollLeft = source.scrollLeft

  requestAnimationFrame(() => {
    targetElement.syncing = false
  })
}


const enhanceMarkdownTables = (root: HTMLElement): void => {
  const tables = root.querySelectorAll<HTMLTableElement>('.markdown-content table')

  tables.forEach((table) => {
    const existingWrap = table.closest('.table-scroll-wrap')
    if (existingWrap) {
      const topInner = existingWrap.querySelector<HTMLElement>(
        '.table-scroll-top-inner',
      )
      if (topInner) {
        topInner.style.width = `${table.scrollWidth}px`
      }
      return
    }

    const parent = table.parentElement
    if (!parent) {
      return
    }

    const wrap = document.createElement('div')
    wrap.className = 'table-scroll-wrap'

    const top = document.createElement('div')
    top.className = 'table-scroll-top'

    const topInner = document.createElement('div')
    topInner.className = 'table-scroll-top-inner'
    topInner.style.width = `${table.scrollWidth}px`
    top.appendChild(topInner)

    const bottom = document.createElement('div')
    bottom.className = 'table-scroll-bottom'

    parent.insertBefore(
      wrap,
      table,
    )
    parent.removeChild(table)
    bottom.appendChild(table)
    wrap.appendChild(top)
    wrap.appendChild(bottom)

    top.addEventListener('scroll', () => {
      syncScroll(
        top,
        bottom,
      )
    })

    bottom.addEventListener('scroll', () => {
      syncScroll(
        bottom,
        top,
      )
    })
  })
}


const refreshMarkdownTableScrollbars = (
  rootRef: Ref<HTMLElement | null>,
): void => {
  nextTick(() => {
    const root = rootRef.value
    if (!root) {
      return
    }
    enhanceMarkdownTables(root)
  })
}


export const useMarkdownTableScrollbars = (
  rootRef: Ref<HTMLElement | null>,
): void => {
  const onWindowResize = (): void => {
    refreshMarkdownTableScrollbars(rootRef)
  }

  onMounted(() => {
    refreshMarkdownTableScrollbars(rootRef)
    window.addEventListener(
      'resize',
      onWindowResize,
    )
  })

  onUpdated(() => {
    refreshMarkdownTableScrollbars(rootRef)
  })

  onBeforeUnmount(() => {
    window.removeEventListener(
      'resize',
      onWindowResize,
    )
  })
}