import { NightwatchBrowser } from 'nightwatch'

module.exports = {
  'Products Page Test': function (browser: NightwatchBrowser) {
    browser
      .url('http://localhost:5173/products')
      .waitForElementVisible('body', 1000)
      .assert.titleContains('Crystal')
      .assert.visible('h1')
      .assert.containsText('h1', 'Products')
      .end()
  },

  'Products Table Test': function (browser: NightwatchBrowser) {
    browser
      .url('http://localhost:5173/products')
      .waitForElementVisible('table', 2000)
      .assert.elementPresent('table')
      .assert.elementPresent('thead')
      .assert.elementPresent('tbody')
      .end()
  },

  'Add Product Button Test': function (browser: NightwatchBrowser) {
    browser
      .url('http://localhost:5173/products')
      .waitForElementVisible('button', 2000)
      .assert.elementPresent('button[class*="bg-blue-600"]')
      .assert.containsText('button[class*="bg-blue-600"]', 'Add Product')
      .end()
  }
} 