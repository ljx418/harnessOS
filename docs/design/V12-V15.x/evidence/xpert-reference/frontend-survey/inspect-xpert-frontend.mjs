import playwright from '../../../../../../apps/workflow-console/node_modules/playwright/index.js'
import { mkdirSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const { chromium } = playwright

const outDir = resolve('docs/design/V12-V15.x/evidence/xpert-reference/frontend-survey')
mkdirSync(outDir, { recursive: true })

const pages = [
  { id: 'onboarding', url: 'http://127.0.0.1:18080/onboarding' },
  { id: 'onboarding-started', url: 'http://127.0.0.1:18080/onboarding', action: 'click-start' },
  { id: 'onboarding-complete-attempt', url: 'http://127.0.0.1:18080/onboarding', action: 'complete-onboarding' },
  { id: 'root', url: 'http://127.0.0.1:18080/' },
  { id: 'chat', url: 'http://127.0.0.1:18080/chat' },
  { id: 'chat-common', url: 'http://127.0.0.1:18080/chat/x/common' },
  { id: 'explore', url: 'http://127.0.0.1:18080/explore' },
  { id: 'plugins', url: 'http://127.0.0.1:18080/settings/plugins' }
]

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({
  viewport: { width: 1440, height: 1000 },
  deviceScaleFactor: 1
})

const results = []

for (const entry of pages) {
  const page = await context.newPage()
  const consoleMessages = []
  const pageErrors = []
  const failedRequests = []
  const responses = []

  page.on('console', (message) => {
    consoleMessages.push({
      type: message.type(),
      text: message.text().slice(0, 1000)
    })
  })
  page.on('pageerror', (error) => {
    pageErrors.push(error.message)
  })
  page.on('requestfailed', (request) => {
    failedRequests.push({
      url: request.url(),
      method: request.method(),
      failure: request.failure()?.errorText ?? 'unknown'
    })
  })
  page.on('response', (response) => {
    const url = response.url()
    if (url.includes('/api/') || url.includes('/assets/') || url.includes('.js') || url.includes('.css')) {
      responses.push({
        url,
        status: response.status()
      })
    }
  })

  const startedAt = new Date().toISOString()
  let navigationError = null
  try {
    await page.goto(entry.url, { waitUntil: 'domcontentloaded', timeout: 30000 })
    await page.waitForTimeout(20000)
    if (entry.action === 'click-start') {
      const button = page.getByRole('button', { name: /get started/i })
      await button.click({ timeout: 5000 })
      await page.waitForTimeout(10000)
    }
    if (entry.action === 'complete-onboarding') {
      const timestamp = Date.now()
      await page.getByRole('button', { name: /get started/i }).click({ timeout: 5000 })
      await page.waitForTimeout(1000)
      const inputs = page.locator('input')
      await inputs.nth(0).fill('HarnessOS')
      await inputs.nth(1).fill('Reviewer')
      await inputs.nth(2).fill(`harnessos.local.${timestamp}@example.com`)
      await inputs.nth(3).fill('HarnessOS Local Review')
      await inputs.nth(4).fill('XpertLocal123!')
      await inputs.nth(5).fill('XpertLocal123!')
      await page.getByRole('button', { name: /^next$/i }).click()
      await page.waitForTimeout(5000)
      const nextButtons = await page.getByRole('button', { name: /^next$|done|finish|complete/i }).all()
      if (nextButtons[0]) {
        await nextButtons[0].click().catch(() => {})
        await page.waitForTimeout(5000)
      }
      const finalButtons = await page.getByRole('button', { name: /done|finish|complete|start|enter/i }).all()
      if (finalButtons[0]) {
        await finalButtons[0].click().catch(() => {})
        await page.waitForTimeout(10000)
      }
    }
  } catch (error) {
    navigationError = error.message
  }

  const screenshotPath = `${outDir}/xpert-${entry.id}-20s.png`
  await page.screenshot({ path: screenshotPath, fullPage: true })

  const title = await page.title().catch(() => '')
  const finalUrl = page.url()
  const bodyText = await page.locator('body').innerText({ timeout: 1000 }).catch(() => '')
  const html = await page.content().catch(() => '')
  const loadingIndicatorCount = await page.locator('text=/loading|Loading|加载/i').count().catch(() => 0)

  results.push({
    id: entry.id,
    url: entry.url,
    final_url: finalUrl,
    title,
    started_at: startedAt,
    screenshot: screenshotPath,
    navigation_error: navigationError,
    body_text_excerpt: bodyText.slice(0, 2000),
    body_text_length: bodyText.length,
    html_length: html.length,
    loading_indicator_count: loadingIndicatorCount,
    console_messages: consoleMessages.slice(0, 60),
    page_errors: pageErrors,
    failed_requests: failedRequests,
    response_errors: responses.filter((response) => response.status >= 400).slice(0, 80),
    api_responses_seen: responses.filter((response) => response.url.includes('/api/')).slice(0, 80)
  })

  await page.close()
}

await browser.close()

const reportPath = `${outDir}/xpert-frontend-survey-results.json`
writeFileSync(reportPath, `${JSON.stringify({ generated_at: new Date().toISOString(), results }, null, 2)}\n`)

const markdownPath = `${outDir}/xpert-frontend-survey-report.md`
writeFileSync(
  markdownPath,
  [
    '# Xpert Frontend Survey Report',
    '',
    `Generated at: ${new Date().toISOString()}`,
    '',
    '## Pages',
    '',
    ...results.map((result) => [
      `### ${result.id}`,
      '',
      `- URL: ${result.url}`,
      `- Final URL: ${result.final_url}`,
      `- Title: ${result.title || '(empty)'}`,
      `- Screenshot: ${result.screenshot}`,
      `- Body text length: ${result.body_text_length}`,
      `- Loading indicators: ${result.loading_indicator_count}`,
      `- Navigation error: ${result.navigation_error || 'none'}`,
      `- Page errors: ${result.page_errors.length}`,
      `- Failed requests: ${result.failed_requests.length}`,
      `- Response errors: ${result.response_errors.length}`,
      '',
      'Body text excerpt:',
      '',
      '```text',
      result.body_text_excerpt || '(empty)',
      '```',
      ''
    ].join('\n'))
  ].join('\n')
)

console.log(reportPath)
console.log(markdownPath)
