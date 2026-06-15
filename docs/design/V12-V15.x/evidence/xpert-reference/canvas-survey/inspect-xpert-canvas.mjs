import playwright from '../../../../../../apps/workflow-console/node_modules/playwright/index.js'
import { mkdirSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const { chromium } = playwright

const baseUrl = 'http://127.0.0.1:18080'
const outDir = resolve('docs/design/V12-V15.x/evidence/xpert-reference/canvas-survey')
mkdirSync(outDir, { recursive: true })

const screenshots = []
const events = []
const email = 'harnessos.local.1781162795459@example.com'
const password = 'XpertLocal123!'
const benchmarkXpertId = 'c5b092e7-1c96-4a37-b23b-84b9b283d8e4'

function pushEvent(type, data = {}) {
  events.push({
    type,
    at: new Date().toISOString(),
    ...data
  })
}

async function snapshot(page, id, note) {
  const path = `${outDir}/${id}.png`
  await page.screenshot({ path, fullPage: true })
  const bodyText = await page.locator('body').innerText({ timeout: 1500 }).catch(() => '')
  screenshots.push({
    id,
    note,
    path,
    url: page.url(),
    title: await page.title().catch(() => ''),
    body_text_excerpt: bodyText.slice(0, 2400),
    body_text_length: bodyText.length
  })
  pushEvent('screenshot', { id, path, url: page.url(), note })
}

async function clickFirstVisible(page, locators, label) {
  for (const locator of locators) {
    const count = await locator.count().catch(() => 0)
    for (let index = 0; index < count; index += 1) {
      const item = locator.nth(index)
      if (await item.isVisible().catch(() => false)) {
        await item.click({ timeout: 5000 })
        pushEvent('click', { label })
        return true
      }
    }
  }
  pushEvent('click-missed', { label })
  return false
}

async function fillVisibleInputs(page, values) {
  const inputs = page.locator('input, textarea')
  const count = await inputs.count().catch(() => 0)
  let valueIndex = 0
  for (let index = 0; index < count && valueIndex < values.length; index += 1) {
    const input = inputs.nth(index)
    if (!(await input.isVisible().catch(() => false))) continue
    const type = await input.getAttribute('type').catch(() => null)
    if (type === 'checkbox' || type === 'radio' || type === 'hidden') continue
    await input.fill(values[valueIndex], { timeout: 3000 }).catch(() => {})
    pushEvent('fill-input', { index, value_label: `value-${valueIndex}` })
    valueIndex += 1
  }
  return valueIndex
}

async function loginIfNeeded(page) {
  await page.goto(`${baseUrl}/auth/login`, { waitUntil: 'domcontentloaded', timeout: 30000 })
  await page.waitForTimeout(3000)
  const bodyText = await page.locator('body').innerText({ timeout: 1500 }).catch(() => '')
  if (!/login|sign in|登录|email|邮箱/i.test(bodyText)) {
    pushEvent('login-skip', { reason: 'no-login-copy-detected', url: page.url() })
    return
  }

  await snapshot(page, 'xpert-login-before', '登录页或认证入口')
  await fillVisibleInputs(page, [email, password])
  await clickFirstVisible(
    page,
    [
      page.getByRole('button', { name: /login|sign in|登录|登入/i }),
      page.locator('button[type="submit"]'),
      page.locator('button')
    ],
    'login-submit'
  )
  await page.waitForTimeout(6000)
  await snapshot(page, 'xpert-login-after', '登录后页面')
}

async function ensureAuthenticated(page, label) {
  if (!/\/auth\/login/.test(page.url())) return
  pushEvent('ensure-auth', { label, url: page.url() })
  await fillVisibleInputs(page, [email, password])
  await clickFirstVisible(
    page,
    [
      page.getByRole('button', { name: /submit|login|sign in|登录|登入/i }),
      page.locator('button[type="submit"]'),
      page.locator('button')
    ],
    `login-submit-${label}`
  )
  await page.waitForTimeout(6000)
  await snapshot(page, `xpert-login-after-${label}`, `登录后页面：${label}`)
}

async function createBlankXpertIfNeeded(page) {
  if (benchmarkXpertId) {
    pushEvent('create-skip', {
      reason: 'using-local-canvas-benchmark-fixture',
      xpert_id: benchmarkXpertId
    })
    return
  }
  await page.goto(`${baseUrl}/xpert/w`, { waitUntil: 'domcontentloaded', timeout: 30000 })
  await page.waitForTimeout(6000)
  await ensureAuthenticated(page, 'workspace')
  if (!/\/xpert\/w/.test(page.url())) {
    await page.goto(`${baseUrl}/xpert/w`, { waitUntil: 'domcontentloaded', timeout: 30000 })
    await page.waitForTimeout(5000)
  }
  await snapshot(page, 'xpert-workspace-before-create', '工作区页，创建 Xpert 前')

  const bodyText = await page.locator('body').innerText({ timeout: 1500 }).catch(() => '')
  if (/Create blank Xpert|创建.*Xpert|Create Xpert/i.test(bodyText)) {
    await clickFirstVisible(
      page,
      [
        page.getByText(/Create blank Xpert/i),
        page.getByText(/Create Xpert/i),
        page.locator('text=/创建.*Xpert/')
      ],
      'create-blank-xpert'
    )
    await page.waitForTimeout(2500)
    await snapshot(page, 'xpert-create-dialog-step0', '创建空白 Xpert 向导起始页')

    await clickFirstVisible(page, [page.getByRole('button', { name: /^Next$/i }), page.getByText(/^Next$/i)], 'wizard-next-0')
    await page.waitForTimeout(1200)
    await snapshot(page, 'xpert-create-dialog-basic', '创建向导基础信息页')
    await fillVisibleInputs(page, [
      `harnessos_canvas_${Date.now()}`,
      'HarnessOS Canvas Benchmark',
      '本地 Xpert 画布体验采集：用于对标 HarnessOS 后续前端工作台。'
    ])

    for (let step = 1; step <= 4; step += 1) {
      const clickedNext = await clickFirstVisible(
        page,
        [page.getByRole('button', { name: /^Next$/i }), page.getByText(/^Next$/i)],
        `wizard-next-${step}`
      )
      await page.waitForTimeout(1000)
      if (!clickedNext) break
    }
    await snapshot(page, 'xpert-create-dialog-before-save', '创建向导保存前')

    await clickFirstVisible(
      page,
      [
        page.getByRole('button', { name: /^Save$/i }),
        page.getByText(/^Save$/i),
        page.getByRole('button', { name: /Create and publish/i })
      ],
      'wizard-save'
    )
    await page.waitForTimeout(9000)
  }
}

async function openCanvasAndInteract(page) {
  if (benchmarkXpertId) {
    await page.goto(`${baseUrl}/xpert/x/${benchmarkXpertId}/agents`, { waitUntil: 'domcontentloaded', timeout: 30000 })
    await page.waitForTimeout(8000)
    await ensureAuthenticated(page, 'direct-canvas')
    if (!/\/xpert\/x\/[^/]+\/agents/.test(page.url())) {
      await page.goto(`${baseUrl}/xpert/x/${benchmarkXpertId}/agents`, { waitUntil: 'domcontentloaded', timeout: 30000 })
      await page.waitForTimeout(8000)
    }
  }

  let canvasUrl = page.url()
  if (!/\/xpert\/x\/[^/]+\/agents/.test(canvasUrl)) {
    await page.goto(`${baseUrl}/xpert/w`, { waitUntil: 'domcontentloaded', timeout: 30000 })
    await page.waitForTimeout(5000)
    await ensureAuthenticated(page, 'open-canvas')
    if (!/\/xpert\/w/.test(page.url())) {
      await page.goto(`${baseUrl}/xpert/w`, { waitUntil: 'domcontentloaded', timeout: 30000 })
      await page.waitForTimeout(5000)
    }
    await clickFirstVisible(page, [page.locator('xpert-card').first(), page.locator('a[href*="/xpert/x/"]').first()], 'open-first-xpert-card')
    await page.waitForTimeout(7000)
    canvasUrl = page.url()
  }

  await snapshot(page, 'xpert-canvas-loaded', 'Xpert 画布页加载结果')

  await clickFirstVisible(
    page,
    [page.getByRole('button', { name: /Agent Settings|智能体设置/i }), page.getByText(/Agent Settings|智能体设置/i)],
    'open-agent-settings'
  )
  await page.waitForTimeout(1500)
  await snapshot(page, 'xpert-canvas-agent-settings', '顶部智能体设置入口')

  await clickFirstVisible(
    page,
    [page.locator('xpert-studio-node-agent').first(), page.locator('[fNode]').first()],
    'select-first-node'
  )
  await page.waitForTimeout(1500)
  await snapshot(page, 'xpert-canvas-node-selected', '选择画布节点后的状态')

  await clickFirstVisible(
    page,
    [page.locator('xpert-studio-toolbar i.ri-add-circle-fill').first(), page.locator('i.ri-add-circle-fill').first()],
    'open-add-menu'
  )
  await page.waitForTimeout(1500)
  await snapshot(page, 'xpert-canvas-add-menu', '底部添加节点菜单')

  await clickFirstVisible(
    page,
    [page.locator('i.ri-node-tree').first(), page.getByText(/Arrange nodes|排列|布局/i)],
    'auto-layout'
  )
  await page.waitForTimeout(1500)
  await snapshot(page, 'xpert-canvas-auto-layout', '自动布局后画布')
}

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({
  viewport: { width: 1728, height: 1117 },
  deviceScaleFactor: 1
})
const page = await context.newPage()

page.on('console', (message) => pushEvent('console', { level: message.type(), text: message.text().slice(0, 1000) }))
page.on('pageerror', (error) => pushEvent('pageerror', { message: error.message }))
page.on('requestfailed', (request) =>
  pushEvent('requestfailed', {
    url: request.url(),
    method: request.method(),
    error: request.failure()?.errorText ?? 'unknown'
  })
)

let fatalError = null
try {
  await loginIfNeeded(page)
  await createBlankXpertIfNeeded(page)
  await openCanvasAndInteract(page)
} catch (error) {
  fatalError = error.stack || error.message
  pushEvent('fatal-error', { message: fatalError })
  await snapshot(page, 'xpert-canvas-fatal-state', '脚本失败时的页面状态').catch(() => {})
}

await browser.close()

const result = {
  generated_at: new Date().toISOString(),
  base_url: baseUrl,
  fatal_error: fatalError,
  screenshots,
  events
}

writeFileSync(`${outDir}/xpert-canvas-survey-results.json`, `${JSON.stringify(result, null, 2)}\n`)
writeFileSync(
  `${outDir}/xpert-canvas-survey-report.md`,
  [
    '# Xpert Canvas Survey Report',
    '',
    `Generated at: ${result.generated_at}`,
    `Fatal error: ${fatalError || 'none'}`,
    '',
    '## Screenshots',
    '',
    ...screenshots.map((shot) => [
      `### ${shot.id}`,
      '',
      `- Note: ${shot.note}`,
      `- URL: ${shot.url}`,
      `- Screenshot: ${shot.path}`,
      `- Body text length: ${shot.body_text_length}`,
      '',
      '```text',
      shot.body_text_excerpt || '(empty)',
      '```',
      ''
    ].join('\n'))
  ].join('\n')
)

console.log(`${outDir}/xpert-canvas-survey-results.json`)
