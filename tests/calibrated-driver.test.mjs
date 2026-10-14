import { readFileSync } from 'node:fs'
import test from 'node:test'
import assert from 'node:assert/strict'
import vm from 'node:vm'

const source = readFileSync(new URL('../firmware-configs/scservo-calibrated-driver.js', import.meta.url), 'utf8')
const defaults = JSON.parse(readFileSync(new URL('../firmware-configs/cores3-scs0009.json', import.meta.url))).config.driver
function setup(overrides = {}) {
  const instances = []
  class Servo {
    constructor(options) { this.options = options; this.position = 512; this.calls = []; instances.push(this) }
    setTorque(enabled, cb) { this.calls.push(['torque', enabled]); cb?.(this.error) }
    setRawPosition(raw, cb) { this.calls.push(['raw', raw]); this.position = raw; cb?.(this.error) }
    setRawPositionInTime(raw, ms, cb) { this.calls.push(['timed', raw, ms]); this.position = raw; cb?.(this.error) }
    readRawPosition(cb) { cb(this.error ? { success: false, reason: this.error.message } : { success: true, value: { position: this.position } }) }
  }
  const context = vm.createContext({ SCServo: Servo })
  const code = source.replace(/import SCServo from 'protocols\/scservo'/, '').replace('export class SCServoDriver', 'class SCServoDriver') + '\nSCServoDriver'
  const Driver = vm.runInContext(code, context)
  return { driver: new Driver({ ...defaults, ...overrides }), instances }
}

test('explicit serial options reach both protocol instances', () => {
  const { instances } = setup()
  assert.deepEqual(instances.map(s => s.options.id), [1, 2])
  for (const s of instances) {
    assert.deepEqual(s.options.serial, defaults.serial)
    assert.equal(s.options.awaitWriteResponse, true)
  }
})
test('300-degree model uses raw scale and converts readback consistently', () => {
  const { driver, instances } = setup()
  driver.applyRotation({ y: 10 * Math.PI / 180, p: -5 * Math.PI / 180 }, 0.5)
  assert.deepEqual(instances[0].calls, [['timed', 478, 500]])
  assert.deepEqual(instances[1].calls, [['timed', 529, 500]])
  driver.getRotation(result => {
    assert.equal(result.success, true)
    assert.ok(Math.abs(result.value.y - 10 * Math.PI / 180) < 0.006)
    assert.ok(Math.abs(result.value.p + 5 * Math.PI / 180) < 0.006)
  })
})
test('large requested angles remain inside configured mechanical limits', () => {
  const { driver, instances } = setup()
  driver.applyRotation({ y: -Math.PI, p: Math.PI }, 0)
  assert.deepEqual(instances[0].calls, [['raw', 546]])
  assert.deepEqual(instances[1].calls, [['raw', 495]])
})
test('axis direction and independently calibrated zero change the correct axis', () => {
  const { driver, instances } = setup({ panDirection: 1, panZeroRaw: 450, tiltZeroRaw: 620 })
  driver.applyRotation({ y: 5 * Math.PI / 180, p: 0 }, 0)
  assert.equal(instances[0].position, 467)
  assert.equal(instances[1].position, 620)
})
test('failed pan command stops the sequence and reports the error', () => {
  const { driver, instances } = setup()
  instances[0].error = new Error('timeout')
  let result
  driver.applyRotation({ y: 0, p: 0 }, 0.5, error => { result = error })
  assert.equal(result.message, 'timeout')
  assert.equal(instances[1].calls.length, 0)
  driver.getRotation(value => assert.equal(value.success, false))
})
test('both axes acknowledge torque changes', () => {
  const { driver, instances } = setup()
  let completed = false
  driver.setTorque(false, error => { assert.equal(error, undefined); completed = true })
  assert.equal(completed, true)
  for (const s of instances) assert.deepEqual(s.calls, [['torque', false]])
})
test('invalid calibration and non-finite motions fail before unsafe writes', () => {
  for (const overrides of [
    { angleRangeDegrees: 0 }, { panDirection: 0 }, { panZeroRaw: -1 },
    { panMin: 1 }, { panMax: 400 }, { panId: 2 }, { serial: undefined },
  ]) assert.throws(() => setup(overrides))
  const { driver, instances } = setup()
  assert.throws(() => driver.applyRotation({ y: NaN, p: 0 }))
  assert.throws(() => driver.applyRotation({ y: 0, p: 0 }, 70))
  assert.equal(instances[0].calls.length, 0)
  assert.equal(instances[1].calls.length, 0)
})
