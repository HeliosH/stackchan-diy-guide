import Timer from 'timer'

export function onContextCreated(robot) {
  const wait = milliseconds => new Promise(resolve => Timer.set(resolve, milliseconds))
  const run = async () => {
    await robot.motion.setTorque(true)
    for (const [yaw, pitch] of [[0, 0], [5, 0], [-5, 0], [0, 3], [0, -3], [0, 0]]) {
      trace(`[diy-smoke] yaw=${yaw} pitch=${pitch}\n`)
      await robot.motion.setPose({
        position: { x: 0, y: 0, z: 0 },
        rotation: { y: yaw * Math.PI / 180, p: pitch * Math.PI / 180, r: 0 },
      }, 0.5)
      await wait(1500)
    }
    await robot.motion.setTorque(false)
    trace('[diy-smoke] complete; disconnect servo power before assembly\n')
  }
  run().catch(error => {
    trace(`[diy-smoke] failed: ${error}\n`)
    robot.motion.setTorque(false).catch(releaseError => trace(`[diy-smoke] release failed: ${releaseError}\n`))
  })
}
