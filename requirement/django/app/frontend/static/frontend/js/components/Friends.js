import { getUserId, addNavigate, fetchJson } from "./utils.js";

export class Friends extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.friends = []
		this.shadowRoot.innerHTML = this.template()
	}

	template = () => {
		return `
			<link rel="stylesheet" href="https://unicons.iconscout.com/release/v4.0.8/css/line.css">
			<link rel="stylesheet" href="${window.location.origin}/static/frontend/js/components/Friends.css">
			
			<div id="Friends">
				<div id="header">
					<h4>Friends</h4>
					<button id="friendRecommendBtn" data-url="recommend-friend" data-title="Baby cadet friend recommend">
						<i class="uil uil-user-plus"></i> Find Friends
					</button>
				</div>
				<table>
					<tbody id="friendTableBody">
					</tbody>
				</table>
			</div>
		`;
	};

	generateRows(friends) {
		return friends.map(
			(friend) => `
			<friend-component 
				id="${friend.username}"
				data-username="${friend.username}" 
				data-id="${friend.id}"
				data-avatar="${friend.avatar}"
			>
			</friend-component>
		`).join('');
	}

	fetchFriends = async () => {
		const result = await fetchJson("fetchFriends", "GET", 
			`/api/users/${getUserId()}/friends`)
		// console.log(result)
		if (result) this.render(result)
		else this.shadowRoot.getElementById('friendTableBody').innerHTML = ""

		// live_chat still bug 
		const dashBoardComponent = document.getElementById("dashBoardComponent")
		let liveChat = dashBoardComponent.shadowRoot.getElementById("liveChatComponent")
		liveChat.remove()
		liveChat = document.createElement('live-chat-component')
		liveChat.setAttribute("id", "liveChatComponent")
		dashBoardComponent.shadowRoot.getElementById("div-right").appendChild(liveChat)
		// liveChat = dashBoardComponent.shadowRoot.getElementById("liveChatComponent")
		
	};

	render(friends) {
		this.shadowRoot.getElementById('friendTableBody')
		.innerHTML = ""
		this.shadowRoot.getElementById('friendTableBody')
			.innerHTML = this.generateRows(friends)

		// add event for each button
		// const parent = this.parentNode.parentNode.parentNode
		// const mainFrame = parent.getElementById("mainFrame")
		// friends.forEach(friend => {
		// 	const friendProfileBtn = this.shadowRoot
		// 		.getElementById(`${friend.username}ProfileBtn`)
		// 	addNavigate(friendProfileBtn, mainFrame)
		// })
	}

	connectedCallback() {
		this.fetchFriends()

		// JavaScript to handle navigation and content loading
		// document.addEventListener('DOMContentLoaded', () => {
			// console.log('DOMContentLoaded')
			const parent = this.parentNode.parentNode.parentNode
			const mainFrame = parent.getElementById("mainFrame")

			// Attach click event listener to navigation items
			const friendRecommendBtn = this.shadowRoot.querySelector('#friendRecommendBtn')
			addNavigate(friendRecommendBtn, mainFrame)
		// })
	}
}
