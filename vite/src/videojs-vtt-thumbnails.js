// make sure videojs plugins are working
import videojs from 'video.js'

// based on https://github.com/Teyuto/videojs-vtt-thumbnails but modified for vite and fixing some things
function vttThumbnails(options) {
    const player = this

    const vttContainer = player.el().querySelector('.thumbnail-preview')
    if (vttContainer) vttContainer.remove()

    const thumbnailContainer = document.createElement('div')
    thumbnailContainer.className = 'thumbnail-preview'

    player.el().appendChild(thumbnailContainer)

    function createThumbnails(url) {
        if (url === undefined) {
            console.error('url is undefined')
            return
        }

        if (typeof url === 'string') {
            fetch(url)
                .then(response => response.text())
                .then(data => processVttData(data))
                .catch(error => console.error('Error fetching VTT data:', error))
        } else {
            console.error('Invalid vttData format')
        }
    }

    function processVttData(vttData) {
        const lines = vttData.split('\n')
        let index = 0

        while (index < lines.length) {
            const line = lines[index].trim()
            if (line !== '') {
                const matchTime = line.match(/(\d+:\d+:\d+[\.,]\d+) --> (\d+:\d+:\d+[\.,]\d+)/)
                if (matchTime) {
                    const [, startTime, endTime] = matchTime
                    const xywhLine = lines[index + 1]
                    const matchSpriteUrlXYWH = xywhLine.match(/(.*)#xywh=(\d+),(\d+),(\d+),(\d+)/)
                    if (matchSpriteUrlXYWH) {
                        const [, spriteUrl, x, y, width, height] = matchSpriteUrlXYWH
                        createThumbnail(spriteUrl, parseVttTime(startTime), x, y, width, height)
                    }
                }
            }
            index += 1
        }
    }

    function createThumbnail(spriteUrl, startTime, x, y, width, height) {
        const thumbnail = document.createElement('div')
        thumbnail.className = 'thumbnail'
        thumbnail.dataset.startTime = startTime

        thumbnail.style.backgroundImage = `url(${spriteUrl})`
        thumbnail.style.backgroundPosition = `-${x}px -${y}px`
        thumbnail.style.width = `${width}px`
        thumbnail.style.height = `${height}px`
        thumbnailContainer.appendChild(thumbnail)
    }

    function parseVttTime(timeString) {
        const match = timeString.match(/(\d+:\d+:\d+[\.,]\d+)/)

        if (match) {
            const [fullMatch] = match
            const timeArray = fullMatch.split(':').map(parseFloat)

            if (Array.isArray(timeArray) && timeArray.length === 3) {
                const [hours, minutes, seconds] = timeArray
                return hours * 3600 + minutes * 60 + seconds
            } else {
                console.error('Error format VTT:', timeString)
                return 0
            }
        } else {
            console.error('Error format VTT:', timeString)
            return 0
        }
    }

    createThumbnails(options.url)

    player.ready(() => {
        player.controlBar.progressControl.on('mousemove', function (e) {
            const progressBar = player.controlBar.progressControl.el()
            const barRect = progressBar.getBoundingClientRect()
            const percentage = (e.clientX - barRect.left) / barRect.width
            const time = percentage * player.duration()

            document.querySelectorAll('.thumbnail').forEach(thumbnail => {
                thumbnail.style.display = 'none'
            })

            const closestThumbnail = findClosestThumbnail(time)
            if (closestThumbnail) {
                closestThumbnail.style.display = 'block'
            }

            const playerRect = player.el().getBoundingClientRect()

            thumbnailContainer.style.left = (e.pageX - playerRect.left) + 'px'
            thumbnailContainer.style.display = 'block'
        })

        player.controlBar.progressControl.on('mouseleave', function () {
            thumbnailContainer.style.display = 'none'
        })
    })

    function findClosestThumbnail(time) {
        const thumbnails = document.querySelectorAll('.thumbnail')
        let closestThumbnail = null
        let minDifference = Infinity

        thumbnails.forEach(thumbnail => {
            const thumbnailTime = parseFloat(thumbnail.dataset.startTime)
            const difference = Math.abs(thumbnailTime - time)

            if (difference < minDifference) {
                minDifference = difference
                closestThumbnail = thumbnail
            }
        })

        return closestThumbnail
    }
}
export default vttThumbnails
videojs.registerPlugin('vttThumbnails', vttThumbnails)