document.addEventListener('DOMContentLoaded', () => {

    const getReviewsSection = () => {
        return document.getElementById('reviews');
    };


    const getCsrfToken = () => {

        const input =
            document.querySelector(
                '#reviews [name="csrfmiddlewaretoken"]'
            );

        return input
            ? input.value
            : '';
    };


    const ajaxHeaders = () => ({
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
    });


    /*
    =====================================================
    Refresh complete review section
    =====================================================
    */

    const refreshReviewSection = async (
        sort = null
    ) => {

        const section =
            getReviewsSection();

        if (!section) {
            return;
        }

        const sectionUrl =
            section.dataset.sectionUrl;

        const sortSelect =
            section.querySelector(
                '#rv-sort-select'
            );

        const selectedSort =
            sort ||
            sortSelect?.value ||
            'newest';

        const url =
            new URL(
                sectionUrl,
                window.location.origin
            );

        url.searchParams.set(
            'sort',
            selectedSort
        );


        const response =
            await fetch(
                url.toString(),
                {
                    headers: {
                        'X-Requested-With':
                            'XMLHttpRequest'
                    }
                }
            );


        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const data =
            await response.json();


        if (!data.success) {
            throw new Error(
                'Unable to refresh reviews.'
            );
        }


        const temp =
            document.createElement(
                'div'
            );

        temp.innerHTML =
            data.html;


        const newSection =
            temp.firstElementChild;


        if (!newSection) {
            throw new Error(
                'Review section HTML is empty.'
            );
        }


        section.replaceWith(
            newSection
        );
    };


    /*
    =====================================================
    Submit / Update Review
    =====================================================
    */

    document.addEventListener(
        'submit',
        async (event) => {

            const form =
                event.target;


            if (
                !form.matches(
                    '#mrv-main-form'
                )
            ) {
                return;
            }


            event.preventDefault();


            const button =
                form.querySelector(
                    'button[type="submit"]'
                );


            if (button) {
                button.disabled = true;
                button.textContent =
                    'Saving...';
            }


            try {

                const response =
                    await fetch(
                        form.action,
                        {
                            method: 'POST',
                            headers:
                                ajaxHeaders(),
                            body:
                                new FormData(form)
                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    console.error(
                        'Review validation error:',
                        data
                    );

                    alert(
                        'Please check your review and try again.'
                    );

                    return;
                }


                /*
                Refresh the complete section.
                This changes Write Review to
                Update Your Review after creation,
                and also displays Delete button.
                */

                await refreshReviewSection();

            } catch (error) {

                console.error(
                    'Submit/update review failed:',
                    error
                );

                alert(
                    'Something went wrong while saving your review.'
                );

            } finally {

                /*
                The section may have been replaced,
                so we don't need to modify the old
                button here.
                */
            }
        }
    );


    /*
    =====================================================
    Delete Review
    =====================================================
    */

    document.addEventListener(
        'click',
        async (event) => {

            const button =
                event.target.closest(
                    '#mrv-delete-btn'
                );


            if (!button) {
                return;
            }


            event.preventDefault();


            const confirmed =
                confirm(
                    'Are you sure you want to delete your review?'
                );


            if (!confirmed) {
                return;
            }


            button.disabled = true;
            button.textContent =
                'Deleting...';


            try {

                const response =
                    await fetch(
                        button.dataset.deleteUrl,
                        {
                            method: 'POST',
                            headers:
                                ajaxHeaders()
                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    console.error(
                        'Delete error:',
                        data
                    );

                    alert(
                        'Unable to delete your review.'
                    );

                    button.disabled = false;
                    button.textContent =
                        'Delete My Review';

                    return;
                }


                await refreshReviewSection();

            } catch (error) {

                console.error(
                    'Delete review failed:',
                    error
                );

                alert(
                    'Something went wrong while deleting your review.'
                );

                button.disabled = false;
                button.textContent =
                    'Delete My Review';
            }
        }
    );


    /*
    =====================================================
    Like / Unlike
    =====================================================
    */

    document.addEventListener(
        'submit',
        async (event) => {

            const form =
                event.target;


            if (
                !form.matches(
                    '.mrv-like-form'
                )
            ) {
                return;
            }


            event.preventDefault();


            const button =
                form.querySelector(
                    'button'
                );


            const countSpan =
                form.querySelector(
                    '.mrv-like-count'
                );


            if (button) {
                button.disabled = true;
            }


            try {

                const response =
                    await fetch(
                        form.action,
                        {
                            method: 'POST',
                            headers:
                                ajaxHeaders()
                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    console.error(
                        'Like error:',
                        data
                    );

                    return;
                }


                if (button) {

                    button.classList.toggle(
                        'is-liked',
                        data.liked
                    );

                }


                if (countSpan) {

                    countSpan.textContent =
                        data.likes_count;

                }


            } catch (error) {

                console.error(
                    'Like/unlike failed:',
                    error
                );

            } finally {

                if (button) {
                    button.disabled = false;
                }

            }
        }
    );


    /*
    =====================================================
    Sort Reviews
    =====================================================
    */

    document.addEventListener(
        'change',
        async (event) => {

            const select =
                event.target;


            if (
                !select.matches(
                    '#rv-sort-select'
                )
            ) {
                return;
            }


            const sort =
                select.value;


            select.disabled = true;


            try {

                await refreshReviewSection(
                    sort
                );


                /*
                Update browser URL without
                reloading the page.
                */

                const url =
                    new URL(
                        window.location.href
                    );


                url.searchParams.set(
                    'sort',
                    sort
                );


                url.searchParams.delete(
                    'offset'
                );


                window.history.replaceState(
                    {},
                    '',
                    url.toString()
                );


            } catch (error) {

                console.error(
                    'Sorting reviews failed:',
                    error
                );

            } finally {

                /*
                The select may have been
                replaced by refreshReviewSection().
                */

            }
        }
    );


    /*
    =====================================================
    Show More Reviews
    =====================================================
    */
/*
=====================================================
SHOW MORE / SHOW ALL / SHOW LESS
=====================================================
*/

document.addEventListener(
    'click',
    async (event) => {

        const moreButton =
            event.target.closest('#rv-show-more');

        const allButton =
            event.target.closest('#rv-show-all');

        const lessButton =
            event.target.closest('#rv-show-less');


        /*
        ================================================
        SHOW MORE
        ================================================
        */

        if (moreButton) {

            event.preventDefault();

            const section =
                getReviewsSection();

            const list =
                document.getElementById(
                    'rv-items-list'
                );

            if (!section || !list) {
                return;
            }


            const loadMoreUrl =
                section.dataset.loadMoreUrl;

            const offset =
                moreButton.dataset.offset;

            const sort =
                moreButton.dataset.sort ||
                'newest';


            const url =
                new URL(
                    loadMoreUrl,
                    window.location.origin
                );


            url.searchParams.set(
                'offset',
                offset
            );

            url.searchParams.set(
                'sort',
                sort
            );


            moreButton.disabled =
                true;

            moreButton.textContent =
                'Loading...';


            try {

                const response =
                    await fetch(
                        url.toString(),
                        {
                            headers: {
                                'X-Requested-With':
                                    'XMLHttpRequest'
                            }
                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {
                    throw new Error(
                        'Unable to load reviews.'
                    );
                }


                if (data.html) {

                    list.insertAdjacentHTML(
                        'beforeend',
                        data.html
                    );

                }


                /*
                There are still reviews.
                */

                if (data.has_more) {

                    moreButton.dataset.offset =
                        data.next_offset;

                    moreButton.disabled =
                        false;

                    moreButton.textContent =
                        'Show More Reviews';

                }


                /*
                All reviews are now loaded.
                */

                else {

                    moreButton.style.display =
                        'none';

                    const allButton =
                        document.getElementById(
                            'rv-show-all'
                        );

                    if (allButton) {
                        allButton.style.display =
                            'none';
                    }

                    const lessButton =
                        document.getElementById(
                            'rv-show-less'
                        );

                    if (lessButton) {
                        lessButton.style.display =
                            'inline-flex';
                    }

                }


            } catch (error) {

                console.error(
                    'Show More failed:',
                    error
                );

                moreButton.disabled =
                    false;

                moreButton.textContent =
                    'Show More Reviews';

            }

            return;
        }


        /*
        ================================================
        SHOW ALL
        ================================================
        */

        if (allButton) {

            event.preventDefault();

            const section =
                getReviewsSection();

            const list =
                document.getElementById(
                    'rv-items-list'
                );

            if (!section || !list) {
                return;
            }


            const loadMoreUrl =
                section.dataset.loadMoreUrl;

            const sort =
                allButton.dataset.sort ||
                'newest';


            /*
            offset=0 + a very large PAGE_SIZE
            is NOT safe because backend still uses
            PAGE_SIZE.

            Instead we repeatedly request pages.
            */

            let offset =
                0;

            let hasMore =
                true;


            allButton.disabled =
                true;

            const moreButtonIfExists =document.getElementById('rv-show-more');


            if (moreButtonIfExists) {
                moreButtonIfExists.disabled =
                    true;
            }


            allButton.textContent =
                'Loading...';


            try {

                /*
                Remove current reviews first.
                */

                list.innerHTML = '';


                while (hasMore) {

                    const url =
                        new URL(
                            loadMoreUrl,
                            window.location.origin
                        );


                    url.searchParams.set(
                        'offset',
                        offset
                    );

                    url.searchParams.set(
                        'sort',
                        sort
                    );


                    const response =
                        await fetch(
                            url.toString(),
                            {
                                headers: {
                                    'X-Requested-With':
                                        'XMLHttpRequest'
                                }
                            }
                        );


                    const data =
                        await response.json();


                    if (
                        !response.ok ||
                        !data.success
                    ) {
                        throw new Error(
                            'Unable to load all reviews.'
                        );
                    }


                    if (data.html) {

                        list.insertAdjacentHTML(
                            'beforeend',
                            data.html
                        );

                    }


                    hasMore =
                        data.has_more;

                    offset =
                        data.next_offset;
                }


                /*
                Hide More and All.
                */

                const moreButton =
                    document.getElementById(
                        'rv-show-more'
                    );

                if (moreButton) {
                    moreButton.style.display =
                        'none';
                }


                allButton.style.display =
                    'none';


                /*
                Show Less.
                */

                const lessButton =
                    document.getElementById(
                        'rv-show-less'
                    );

                if (lessButton) {

                    lessButton.style.display =
                        'inline-flex';

                }


            } catch (error) {

                console.error(
                    'Show All failed:',
                    error
                );

                allButton.disabled =
                    false;

                allButton.textContent =
                    'Show All Reviews';

            }

            return;
        }


        /*
        ================================================
        SHOW LESS
        ================================================
        */

        if (lessButton) {

            event.preventDefault();

            const section =
                getReviewsSection();

            if (!section) {
                return;
            }


            const loadMoreUrl =
                section.dataset.loadMoreUrl;

            const sort =
                lessButton.dataset.sort ||
                'newest';


            lessButton.disabled =
                true;

            lessButton.textContent =
                'Loading...';


            try {

                const url =
                    new URL(
                        loadMoreUrl,
                        window.location.origin
                    );


                /*
                Load the first page again.
                */

                url.searchParams.set(
                    'offset',
                    '0'
                );

                url.searchParams.set(
                    'sort',
                    sort
                );


                const response =
                    await fetch(
                        url.toString(),
                        {
                            headers: {
                                'X-Requested-With':
                                    'XMLHttpRequest'
                            }
                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {
                    throw new Error(
                        'Unable to show less reviews.'
                    );
                }


                const list =
                    document.getElementById(
                        'rv-items-list'
                    );


                if (list) {

                    list.innerHTML =
                        data.html;

                }


                /*
                Reset Show More.
                */

                const moreButton =
                    document.getElementById(
                        'rv-show-more'
                    );

                if (moreButton) {

                    moreButton.dataset.offset =
                        data.next_offset;

                    moreButton.dataset.sort =
                        sort;

                    moreButton.style.display =
                        'inline-flex';

                    moreButton.disabled =
                        false;

                    moreButton.textContent =
                        'Show More Reviews';

                }


                /*
                Show All again.
                */

                const allButton =
                    document.getElementById(
                        'rv-show-all'
                    );

                if (allButton) {

                    allButton.dataset.offset =
                        data.next_offset;

                    allButton.dataset.sort =
                        sort;

                    allButton.style.display =
                        'inline-flex';

                    allButton.disabled =
                        false;

                    allButton.textContent =
                        'Show All Reviews';

                }


                /*
                Hide Show Less.
                */

                lessButton.style.display =
                    'none';

                lessButton.disabled =
                    false;

                lessButton.textContent =
                    'Show Less Reviews';


            } catch (error) {

                console.error(
                    'Show Less failed:',
                    error
                );

                lessButton.disabled =
                    false;

                lessButton.textContent =
                    'Show Less Reviews';

            }

        }

    }
);

});
