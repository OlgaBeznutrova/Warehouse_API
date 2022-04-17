import sqlalchemy as sa
from dictalchemy import DictableModel
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base(cls=DictableModel)


class User(Base):
    __tablename__ = "user"
    id = sa.Column(INTEGER(unsigned=True), primary_key=True)
    username = sa.Column(sa.String(20), unique=True, nullable=False)
    password_hash = sa.Column(sa.Text, nullable=False)
    email = sa.Column(sa.String(50), unique=True, nullable=False)
    category = sa.Column(sa.Enum("seller", "buyer"), nullable=False)

    products = relationship("Product", backref="user", passive_deletes=True)


class Product(Base):
    __tablename__ = "product"
    id = sa.Column(INTEGER(unsigned=True), primary_key=True)
    title = sa.Column(sa.String(20), nullable=False)
    quantity = sa.Column(SMALLINT(unsigned=True), nullable=False, default=0)
    price = sa.Column(sa.DECIMAL(10, 2), nullable=False)
    description = sa.Column(sa.String(100))
    user_id = sa.Column(
        INTEGER(unsigned=True),
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    __table_args__ = (sa.UniqueConstraint("title", "user_id", name="unique_title_user"),)


if __name__ == "__main__":
    from database import engine, Session

    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    data = [
        User(username="user1", password_hash="$2b$12$aYO925kNdUXXAkkc7CdT9us.tj75wXEhwkVU5tKUJl.k.bA0kP8cm",
             email="user1@gmail.com", category="seller"),
        User(username="user2", password_hash="$2b$12$KAYca4U73NuKDY.ZFuQSieKrsOSjmmN7uMDg1aQZ862/wuzZMv0yW",
             email="user2@gmail.com", category="buyer"),
        Product(title="apple", quantity=10, price=100, description="Apple description", user_id=1),
        Product(title="pear", quantity=0, price=120, user_id=1)
    ]
    session = Session()
    session.add_all(data)
    session.commit()
    session.close()
