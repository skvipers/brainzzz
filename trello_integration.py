#!/usr/bin/env python3
"""
Trello Integration Script for Brainzzz Project

This script creates Trello cards based on project tasks and brain visualization
features. Requires Trello API Key and Token for authentication.

Usage:
    python trello_integration.py

Setup:
    1. Go to https://trello.com/power-ups/admin/
    2. Create a new Power-Up and get API Key
    3. Generate a token with read/write permissions
    4. Set environment variables or update the script with your credentials
"""

import os
from typing import Dict, List, Optional

import requests

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print(
        "💡 Для автоматической загрузки .env файла установите: "
        "pip install python-dotenv"
    )


class TrelloClient:
    """Simple Trello API client for creating cards and managing boards."""

    def __init__(self, api_key: str, token: str):
        self.api_key = api_key
        self.token = token
        self.base_url = "https://api.trello.com/1"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict:
        """Make authenticated request to Trello API."""
        url = f"{self.base_url}/{endpoint}"

        # Add authentication to params
        if params is None:
            params = {}
        params.update({"key": self.api_key, "token": self.token})

        response = requests.request(method, url, params=params, json=data)
        response.raise_for_status()
        return response.json()

    def get_boards(self) -> List[Dict]:
        """Get all boards for the authenticated user."""
        return self._make_request("GET", "members/me/boards")

    def get_lists(self, board_id: str) -> List[Dict]:
        """Get all lists for a specific board."""
        return self._make_request("GET", f"boards/{board_id}/lists")

    def create_card(
        self,
        list_id: str,
        name: str,
        desc: str = "",
        due: str = None,
        labels: List[str] = None,
    ) -> Dict:
        """Create a new card in the specified list."""
        data = {"name": name, "desc": desc, "idList": list_id}

        if due:
            data["due"] = due

        if labels:
            data["idLabels"] = ",".join(labels)

        return self._make_request("POST", "cards", data=data)

    def create_board(self, name: str, desc: str = "") -> Dict:
        """Create a new board."""
        data = {"name": name, "desc": desc}
        return self._make_request("POST", "boards", data=data)

    def create_list(self, board_id: str, name: str, pos: str = "bottom") -> Dict:
        """Create a new list in the specified board."""
        data = {"name": name, "idBoard": board_id, "pos": pos}
        return self._make_request("POST", "lists", data=data)


def create_brainzzz_cards(client: TrelloClient, board_id: str) -> None:
    """Create cards for Brainzzz project tasks."""

    # Get lists from the board
    lists = client.get_lists(board_id)

    # If no lists found, create default lists
    if not lists:
        print("📝 Списки не найдены. Создаю стандартные списки...")
        try:
            # Create standard Kanban lists
            todo_list = client.create_list(board_id, "📋 To Do")
            in_progress_list = client.create_list(board_id, "🔄 In Progress")
            done_list = client.create_list(board_id, "✅ Done")

            lists = [todo_list, in_progress_list, done_list]
            print(f"✅ Созданы списки: {[lst['name'] for lst in lists]}")
        except Exception as e:
            print(f"❌ Ошибка создания списков: {e}")
            return

    # Use the first list or find "To Do" list
    target_list = lists[0]
    for lst in lists:
        if lst["name"].lower() in ["to do", "todo", "backlog", "идеи", "задачи"]:
            target_list = lst
            break

    print(f"📝 Создаю карточки в списке: {target_list['name']}")

    # Define cards to create
    cards_to_create = [
        {
            "name": "🧠 Fix Cytoscape Visualization Issues",
            "desc": """**Completed ✅**

Fixed the issue where brain connections (edges) were not displaying in the
Cytoscape visualization.

**Problem**: Duplicate edge IDs were causing Cytoscape to fail when adding
connections.
**Solution**: Changed edge ID generation from `conn.id.toString()` to
`edge_${conn.id}_${conn.from}_${conn.to}` for unique identification.

**Technical Details**:
- File: `web/frontend/src/components/BrainVisualizer.tsx`
- Root cause: Multiple connections between same nodes with different backend IDs
- Result: All 11 connections now display correctly with proper colors""",
        },
        {
            "name": "🎨 Improve Brain Visualization UI",
            "desc": """Enhance the brain visualization interface with better user
experience.

**Tasks**:
- [ ] Add connection weight labels toggle
- [ ] Implement node selection highlighting
- [ ] Add zoom controls and minimap
- [ ] Improve color scheme for different connection types
- [ ] Add animation for brain activity simulation

**Priority**: Medium
**Estimated effort**: 2-3 days""",
        },
        {
            "name": "🔧 Clean Up Debug Logging",
            "desc": """Remove excessive debug logging from BrainVisualizer component.

**Current Issue**: Too many console.log statements making development console
noisy.

**Tasks**:
- [ ] Remove diagnostic logs from successful operations
- [ ] Keep only error and warning logs
- [ ] Add optional debug mode flag
- [ ] Implement proper logging levels

**Priority**: Low
**Estimated effort**: 1 hour""",
        },
        {
            "name": "📊 Add Real-time Brain Metrics Dashboard",
            "desc": """Create a real-time dashboard showing brain evolution metrics.

**Features to implement**:
- [ ] Population fitness over time
- [ ] Connection strength distribution
- [ ] Node activation patterns
- [ ] Evolution generation statistics
- [ ] Performance metrics (simulation speed, memory usage)

**Technical Requirements**:
- WebSocket integration for real-time updates
- Chart.js or similar for data visualization
- Redis pub/sub for event streaming

**Priority**: High
**Estimated effort**: 1 week""",
        },
        {
            "name": "🧬 Implement Advanced Evolution Algorithms",
            "desc": """Enhance the evolution engine with more sophisticated algorithms.

**Planned Features**:
- [ ] Speciation (NEAT-style)
- [ ] Novelty search
- [ ] Multi-objective optimization
- [ ] Coevolution between species
- [ ] Dynamic topology mutations

**Research Areas**:
- NeuroEvolution of Augmenting Topologies (NEAT)
- HyperNEAT for large-scale networks
- ES-HyperNEAT for substrate patterns

**Priority**: High
**Estimated effort**: 2-3 weeks""",
        },
        {
            "name": "🚀 Performance Optimization",
            "desc": """Optimize the simulation performance for larger populations
and longer runs.

**Optimization Targets**:
- [ ] Parallel brain evaluation using Ray
- [ ] Memory management for large populations
- [ ] GPU acceleration for neural network operations
- [ ] Efficient genome representation
- [ ] Faster fitness evaluation

**Current Bottlenecks**:
- Brain evaluation in single thread
- Memory leaks in long runs
- Inefficient connection matrix operations

**Priority**: Medium
**Estimated effort**: 1-2 weeks""",
        },
        {
            "name": "📱 Mobile-Friendly Web Interface",
            "desc": """Make the web interface responsive and mobile-friendly.

**Requirements**:
- [ ] Responsive design for tablets and phones
- [ ] Touch-friendly controls for brain visualization
- [ ] Optimized layout for small screens
- [ ] Progressive Web App (PWA) features
- [ ] Offline mode for viewing saved data

**Technical Stack**:
- Tailwind CSS responsive utilities
- Touch gesture support for Cytoscape
- Service Worker for PWA

**Priority**: Low
**Estimated effort**: 1 week""",
        },
        {
            "name": "🔐 Add Authentication and User Management",
            "desc": """Implement user authentication and multi-user support.

**Features**:
- [ ] User registration and login
- [ ] Personal brain collections
- [ ] Shared experiments and results
- [ ] Permission system for collaborative work
- [ ] User preferences and settings

**Technical Implementation**:
- JWT-based authentication
- User database schema
- Session management
- Role-based access control

**Priority**: Medium
**Estimated effort**: 1-2 weeks""",
        },
        {
            "name": "📈 Add Experiment Tracking and Analysis",
            "desc": """Implement comprehensive experiment tracking and statistical
analysis.

**Features**:
- [ ] Experiment versioning and comparison
- [ ] Statistical significance testing
- [ ] Hyperparameter optimization tracking
- [ ] Result visualization and reporting
- [ ] Export capabilities (CSV, JSON, plots)

**Analysis Tools**:
- Population diversity metrics
- Convergence analysis
- Performance correlation studies
- Genetic drift detection

**Priority**: Medium
**Estimated effort**: 2 weeks""",
        },
        {
            "name": "🌐 Add More Task Types and Environments",
            "desc": """Expand the task suite with more challenging environments.

**New Task Types**:
- [ ] Image classification tasks
- [ ] Reinforcement learning environments
- [ ] Time series prediction
- [ ] Multi-agent coordination tasks
- [ ] Continuous control problems

**Integration**:
- OpenAI Gym compatibility
- Custom task definition framework
- Curriculum learning support
- Automated difficulty progression

**Priority**: High
**Estimated effort**: 2-3 weeks""",
        },
    ]

    # Create cards
    created_cards = []
    for card_data in cards_to_create:
        try:
            card = client.create_card(
                list_id=target_list["id"],
                name=card_data["name"],
                desc=card_data["desc"],
            )
            created_cards.append(card)
            print(f"✅ Создана карточка: {card_data['name']}")
        except Exception as e:
            print(f"❌ Ошибка создания карточки '{card_data['name']}': {e}")

    print(f"\n🎉 Создано карточек: {len(created_cards)}/{len(cards_to_create)}")
    return created_cards


def main():
    """Main function to create Trello cards."""

    # Get credentials from environment or prompt user
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    board_id = os.getenv("TRELLO_BOARD_ID")

    if not api_key:
        print("🔑 Trello API Key не найден в переменных окружения.")
        print("Получите API Key здесь: https://trello.com/power-ups/admin/")
        api_key = input("Введите Trello API Key: ").strip()

    if not token:
        print("🎫 Trello Token не найден в переменных окружения.")
        print("\n📋 Для получения токена:")
        print("1. Перейдите по ссылке:")
        print(
            f"   https://trello.com/1/authorize?expiration=never&scope=read,write&"
            f"response_type=token&key={api_key}"
        )
        print("2. Нажмите 'Allow' для разрешения доступа")
        print("3. Скопируйте токен с открывшейся страницы")
        print("\n💡 Для сохранения в переменных окружения создайте файл .env:")
        print(f"   TRELLO_API_KEY={api_key}")
        print("   TRELLO_TOKEN=ваш_токен_здесь")
        print("   TRELLO_BOARD_ID=id_вашей_доски")
        token = input("\nВведите Trello Token: ").strip()

    # Initialize client
    client = TrelloClient(api_key, token)

    try:
        # Get user's boards
        boards = client.get_boards()
        print(f"📋 Найдено досок: {len(boards)}")

        # If board_id not specified, let user choose
        if not board_id:
            print("\nДоступные доски:")
            for i, board in enumerate(boards[:10]):  # Show first 10 boards
                print(f"  {i+1}. {board['name']} (ID: {board['id']})")
            print("  0. 🆕 Создать новую доску 'Brainzzz Project'")

            choice = input(
                "\nВыберите доску (номер), введите ID доски, или 0 для создания новой: "
            ).strip()

            if choice == "0":
                # Create new board
                print("🆕 Создаю новую доску...")
                new_board = client.create_board(
                    name="Brainzzz Project",
                    desc="AI Brain Evolution Simulation - Task Management Board",
                )
                board_id = new_board["id"]
                print(f"✅ Создана новая доска: {new_board['name']} (ID: {board_id})")
            elif choice.isdigit() and 1 <= int(choice) <= len(boards):
                board_id = boards[int(choice) - 1]["id"]
            else:
                board_id = choice

        # Create cards
        print("\n🚀 Создаю карточки для проекта Brainzzz...")
        create_brainzzz_cards(client, board_id)

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка API: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()
