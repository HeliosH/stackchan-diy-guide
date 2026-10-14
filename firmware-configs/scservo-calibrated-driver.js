// Apache-2.0. Guide-owned driver for the Stack-chan v1.1.0 motion interface.
// Use raw positions so the upstream protocol's fixed 200-degree scale is bypassed.
import SCServo from 'protocols/scservo'

const RAD_TO_DEG = 180 / Math.PI

function finite(value, name) {
  if (!Number.isFinite(value)) throw new Error(`${name} must be finite`)
  return value
}

function axis(config, name, travel) {
  const zero = finite(config[`${name}ZeroRaw`], `${name}ZeroRaw`)
  const direction = config[`${name}Direction`] ?? -1
  const min = finite(config[`${name}Min`], `${name}Min`)
  const max = finite(config[`${name}Max`], `${name}Max`)
  if (!Number.isInteger(zero) || zero < 0 || zero > 1023 || ![-1, 1].includes(direction)) {
    throw new Error(`${name}: invalid zero or direction`)
  }
  if (min > 0 || max < 0 || min >= max) throw new Error(`${name}: limits must bracket zero`)
  for (const degrees of [min, max]) {
    const raw = zero + direction * degrees * 1024 / travel
    if (raw < 0 || raw > 1023) throw new Error(`${name}: limits exceed raw position range`)
  }
  return { zero, direction, min, max }
}

export class SCServoDriver {
  constructor(config) {
    this.travel = finite(config.angleRangeDegrees, 'angleRangeDegrees')
    if (this.travel <= 0 || this.travel > 360) throw new Error('invalid angleRangeDegrees')
    this.panAxis = axis(config, 'pan', this.travel)
    this.tiltAxis = axis(config, 'tilt', this.travel)
    if (!Number.isInteger(config.panId) || !Number.isInteger(config.tiltId) ||
        config.panId < 1 || config.tiltId < 1 || config.panId > 253 || config.tiltId > 253 ||
        config.panId === config.tiltId) throw new Error('distinct servo IDs in 1..253 required')
    if (!config.serial) throw new Error('driver.serial is required by the calibrated driver')
    this.pan = new SCServo({ id: config.panId, serial: config.serial, awaitWriteResponse: true })
    this.tilt = new SCServo({ id: config.tiltId, serial: config.serial, awaitWriteResponse: true })
  }

  setTorque(enabled, callback) {
    this.pan.setTorque(enabled, error => {
      if (error != null) { callback?.(error); return }
      this.tilt.setTorque(enabled, callback)
    })
  }

  toRaw(radians, axisConfig) {
    const degrees = Math.max(axisConfig.min, Math.min(axisConfig.max, finite(radians, 'rotation') * RAD_TO_DEG))
    return Math.round(axisConfig.zero + axisConfig.direction * degrees * 1024 / this.travel)
  }

  applyRotation(rotation, seconds = 0.5, callback) {
    const pan = this.toRaw(rotation.y, this.panAxis)
    const tilt = this.toRaw(rotation.p, this.tiltAxis)
    finite(seconds, 'duration')
    // The SCS position command has an unsigned 16-bit millisecond duration.
    if (seconds < 0 || seconds > 65.535) throw new Error('duration outside 0..65.535 seconds')
    const milliseconds = Math.round(seconds * 1000)
    const write = (servo, raw, done) => milliseconds === 0
      ? servo.setRawPosition(raw, done)
      : servo.setRawPositionInTime(raw, milliseconds, done)
    write(this.pan, pan, error => {
      if (error != null) { callback?.(error); return }
      write(this.tilt, tilt, callback)
    })
  }

  getRotation(callback) {
    this.pan.readRawPosition(pan => {
      if (!pan.success) { callback(pan); return }
      this.tilt.readRawPosition(tilt => {
        if (!tilt.success) { callback(tilt); return }
        const angle = (raw, a) => (raw - a.zero) * this.travel / (1024 * a.direction * RAD_TO_DEG)
        callback({ success: true, value: {
          y: angle(pan.value.position, this.panAxis),
          p: angle(tilt.value.position, this.tiltAxis), r: 0,
        } })
      })
    })
  }
}
