document.addEventListener("DOMContentLoaded", () => {
    const postsContainer = document.getElementById('posts-list'); 
    const postForm = document.getElementById('post-form');

    loadPosts();

    postForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const content = document.getElementById('post-content').value;

        const response = await fetch('/api/posts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content }),
        });

        if (response.ok) {
            document.getElementById('post-content').value = ''; 
            loadPosts(); 
        } else {
            alert('Failed to post content');
        }
    });

    function loadPosts() {
        fetch('/api/posts')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                postsContainer.innerHTML = ''; 
                data.posts.forEach(post => {
                    const postElement = document.createElement('div');
                    postElement.classList.add('post');
                    postElement.innerHTML = `
                        <strong>${post.username}:</strong> ${post.content}
                        <div class="timestamp">Posted on ${post.created_at}</div>
                        <div class="comments-list" id="comments-${post.id}">
                            <!-- Comments will be dynamically inserted here -->
                        </div>
                        <form class="comment-form" data-post-id="${post.id}">
                            <input type="text" class="comment-input" placeholder="Add a comment..." required />
                            <button type="submit">Comment</button>
                        </form>
                    `;
                    postsContainer.appendChild(postElement);
    
                    loadComments(post.id);
                });
            })
            .catch(error => {
                console.error('Error loading posts:', error);
                postsContainer.innerHTML = '<p>Error loading posts. Please try again later.</p>';
            });
    }

    function loadComments(postId) {
        fetch(`/api/comments/${postId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const commentsList = document.getElementById(`comments-${postId}`);
                commentsList.innerHTML = '';
                data.comments.forEach(comment => {
                    const commentElement = document.createElement('div');
                    commentElement.classList.add('comment');
                    commentElement.innerHTML = `
                        <strong>${comment.username}:</strong> ${comment.content}
                        <div class="timestamp">Commented on ${comment.created_at}</div>
                    `;
                    commentsList.appendChild(commentElement);
                });

                const commentForm = document.querySelector(`.comment-form[data-post-id="${postId}"]`);
                commentForm.onsubmit = async (e) => { 
                    e.preventDefault();
                    const commentInput = commentForm.querySelector('.comment-input');
                    const commentContent = commentInput.value;

                    const response = await fetch(`/api/comments/${postId}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ content: commentContent }),
                    });

                    if (response.ok) {
                        commentInput.value = '';
                        loadComments(postId);
                    } else {
                        alert('Failed to post comment');
                    }
                };
            })
            .catch(error => {
                console.error(`Error loading comments for post ${postId}:`, error);
                const commentsList = document.getElementById(`comments-${postId}`);
                commentsList.innerHTML = '<p>Error loading comments. Please try again later.</p>';
            });
    }

});